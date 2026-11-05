# source ~/venvs/whisperx311/bin/activate
# which python
# python --version
# python extract_twitch_1.py

import os
import gc
import re
import json
import shutil
import subprocess
from datetime import timedelta

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from bs4 import BeautifulSoup

import torch
import whisperx


# =========================================================
# 0. PARAMETERS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEO_URL = "https://www.twitch.tv/videos/2717414317"
LANGUAGE = "fr"

# Root folder containing one isolated subfolder per Twitch VOD
ARCHIVE_DIR = os.path.join(BASE_DIR, "twitch_archive")

# Recommended: prevents collisions when two VODs have the same title
INCLUDE_VOD_ID_IN_FOLDER = True

# Twitch auth for subscriber-only VODs
TWITCH_COOKIES_FROM_BROWSER = "chrome"  # "chrome", "firefox", "safari", or None

# TwitchDownloaderCLI path
TWITCHDOWNLOADER_CLI = os.path.join(
    BASE_DIR,
    "tools",
    "TwitchDownloaderCLI"
)

TWITCHDOWNLOADER_OAUTH = None  # example: "oauth:xxxxxxxxxxxxxxxx"

# ---------------------------------------------------------
# SAMPLE WINDOW
# Leave both as None for a full-only run
# ---------------------------------------------------------
SAMPLE_START = "00:27:46"  # e.g. "00:22:13" or None
SAMPLE_END = "00:28:58"    # e.g. "00:23:22" or None

HAS_SAMPLE_WINDOW = bool(SAMPLE_START and SAMPLE_END)

# Optional clip extraction for human viewing only
EXTRACT_VIDEO_CLIP = HAS_SAMPLE_WINDOW

# Reuse existing files when available, but only inside the
# directory belonging to the current Twitch VOD
REUSE_EXISTING_VIDEO = True
REUSE_EXISTING_FULL_CHAT_HTML = True
REUSE_EXISTING_FULL_WAV = True
REUSE_EXISTING_VIDEO_CLIP = True
REUSE_EXISTING_FULL_TRANSCRIPTION_CSV = True

# WhisperX settings
WHISPER_MODEL = "small"
BATCH_SIZE = 2
MERGE_TOLERANCE_SECONDS = 2.0

# ---------------------------------------------------------
# FULL FILE NAMES
# ---------------------------------------------------------
FULL_CHAT_HTML_NAME = "chat_full.html"
FULL_CHAT_CSV_NAME = "twitch_full_chat.csv"
FULL_TRANSCRIPTION_CSV_NAME = "twitch_full_transcription.csv"
FULL_MERGED_CSV_NAME = "twitch_full_merged.csv"

# ---------------------------------------------------------
# SAMPLE FILE NAMES
# ---------------------------------------------------------
if HAS_SAMPLE_WINDOW:
    SAMPLE_SUFFIX = (
        f"{SAMPLE_START.replace(':', '-')}_"
        f"{SAMPLE_END.replace(':', '-')}"
    )
else:
    SAMPLE_SUFFIX = "full"

MERGED_HTML_NAME = f"twitch_{SAMPLE_SUFFIX}.html"
MERGED_HTML_PSEUDONYMIZED_NAME = (
    f"twitch_{SAMPLE_SUFFIX}_pseudonymised.html"
)
MERGED_CSV_NAME = f"twitch_{SAMPLE_SUFFIX}_merged_output.csv"
DENSITY_PNG_NAME = f"twitch_{SAMPLE_SUFFIX}_message_density.png"


# =========================================================
# 1. BASIC INFO / CHECKS
# =========================================================

def print_versions():
    print("torch:", torch.__version__)

    try:
        import transformers
        print("transformers:", transformers.__version__)
    except Exception as exc:
        print("transformers: import failed:", exc)


def ensure_command_exists(command_name_or_path):
    if os.path.sep in command_name_or_path or os.path.isabs(
        command_name_or_path
    ):
        if not os.path.isfile(command_name_or_path):
            raise FileNotFoundError(
                f"Required executable not found: {command_name_or_path}"
            )

        if not os.access(command_name_or_path, os.X_OK):
            raise PermissionError(
                f"File exists but is not executable: "
                f"{command_name_or_path}"
            )
    else:
        if shutil.which(command_name_or_path) is None:
            raise FileNotFoundError(
                f"Required command not found in PATH: "
                f"{command_name_or_path}"
            )


# =========================================================
# 2. TIME HELPERS
# =========================================================

def string_to_seconds(time_str):
    if pd.isnull(time_str):
        return None

    time_str = str(time_str).strip()

    if not time_str:
        return None

    negative = time_str.startswith("-")

    if negative:
        time_str = time_str[1:]

    parts = time_str.split(":")

    try:
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
        elif len(parts) == 2:
            hours = 0
            minutes = int(parts[0])
            seconds = float(parts[1])
        else:
            return None

        total = timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        ).total_seconds()

        return -total if negative else total

    except ValueError:
        return None


def extract_twitch_vod_id(video_url):
    match = re.search(r"/videos/(\d+)", video_url)

    if not match:
        raise ValueError(
            f"Could not extract Twitch VOD ID from URL: {video_url}"
        )

    return match.group(1)


def filter_df_by_time_window(
    df,
    start_time,
    end_time,
    rebase_to_zero=True
):
    if df.empty:
        return df.copy()

    start_sec = string_to_seconds(start_time)
    end_sec = string_to_seconds(end_time)

    if (
        start_sec is None
        or end_sec is None
        or end_sec < start_sec
    ):
        raise ValueError("Invalid sample timestamps.")

    out = df.copy()
    out["time"] = pd.to_numeric(
        out["time"],
        errors="coerce"
    )

    out = out.dropna(subset=["time"])

    out = out[
        (out["time"] >= start_sec)
        & (out["time"] <= end_sec)
    ].copy()

    if rebase_to_zero:
        out["time"] = out["time"] - start_sec

    return out.reset_index(drop=True)


# =========================================================
# 3. VOD METADATA AND DIRECTORY CREATION
# =========================================================

def sanitize_filename(value, max_length=150):
    """
    Convert a Twitch title into a safe folder or file name.
    """
    value = str(value).strip()

    # Replace invalid or problematic filename characters
    value = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        value
    )

    # Collapse repeated whitespace and underscores
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"_+", "_", value)

    # Remove trailing spaces, periods, and underscores
    value = value.strip(" ._")

    if not value:
        value = "untitled_twitch_video"

    return value[:max_length].rstrip(" ._")


def get_twitch_video_metadata(
    video_url,
    cookies_from_browser=None
):
    """
    Retrieve Twitch VOD metadata before downloading the video.
    """
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--skip-download",
        "--no-playlist",
    ]

    if cookies_from_browser:
        cmd += [
            "--cookies-from-browser",
            cookies_from_browser
        ]

    cmd.append(video_url)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("yt-dlp metadata stdout:\n", result.stdout)
        print("yt-dlp metadata stderr:\n", result.stderr)

        raise RuntimeError(
            "Could not retrieve Twitch video metadata"
        )

    try:
        metadata = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "yt-dlp returned invalid metadata JSON"
        ) from exc

    vod_id = str(
        metadata.get("id")
        or extract_twitch_vod_id(video_url)
    )

    title = (
        metadata.get("title")
        or f"twitch_vod_{vod_id}"
    )

    uploader = (
        metadata.get("uploader")
        or metadata.get("channel")
        or ""
    )

    return {
        "id": vod_id,
        "title": title,
        "uploader": uploader,
    }


def create_video_directories(
    video_url,
    cookies_from_browser=None
):
    """
    Create an isolated folder structure for one Twitch VOD.
    """
    metadata = get_twitch_video_metadata(
        video_url,
        cookies_from_browser=cookies_from_browser
    )

    safe_title = sanitize_filename(metadata["title"])

    if INCLUDE_VOD_ID_IN_FOLDER:
        folder_name = f"{safe_title}__{metadata['id']}"
    else:
        folder_name = safe_title

    video_root_dir = os.path.join(
        ARCHIVE_DIR,
        folder_name
    )

    downloads_dir = os.path.join(
        video_root_dir,
        "downloads"
    )

    chat_dir = os.path.join(
        video_root_dir,
        "chat"
    )

    output_dir = os.path.join(
        video_root_dir,
        "results"
    )

    for directory in (
        ARCHIVE_DIR,
        video_root_dir,
        downloads_dir,
        chat_dir,
        output_dir,
    ):
        os.makedirs(directory, exist_ok=True)

    metadata_json_path = os.path.join(
        video_root_dir,
        "vod_metadata.json"
    )

    if not os.path.exists(metadata_json_path):
        with open(
            metadata_json_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {
                    "video_url": video_url,
                    **metadata,
                },
                file,
                ensure_ascii=False,
                indent=2
            )

    return {
        "metadata": metadata,
        "video_root_dir": video_root_dir,
        "downloads_dir": downloads_dir,
        "chat_dir": chat_dir,
        "output_dir": output_dir,
    }


# =========================================================
# 4. DOWNLOAD TWITCH VIDEO
# =========================================================

def find_latest_nonclip_mp4(downloads_dir):
    """
    Search only inside the current VOD directory.
    """
    all_mp4 = []

    if not os.path.isdir(downloads_dir):
        return None

    for root, _, files in os.walk(downloads_dir):
        for filename in files:
            full_path = os.path.join(
                root,
                filename
            )

            if (
                full_path.lower().endswith(".mp4")
                and "_clip_" not in os.path.basename(
                    full_path
                )
            ):
                all_mp4.append(full_path)

    if not all_mp4:
        return None

    all_mp4.sort(
        key=os.path.getmtime,
        reverse=True
    )

    return all_mp4[0]


def download_twitch_video(
    video_url,
    output_template,
    downloads_dir,
    cookies_from_browser=None
):
    os.makedirs(downloads_dir, exist_ok=True)

    if REUSE_EXISTING_VIDEO:
        existing = find_latest_nonclip_mp4(
            downloads_dir
        )

        if existing:
            print(
                "Reusing existing video:",
                existing
            )
            return existing

    before = set()

    for root, _, files in os.walk(downloads_dir):
        for filename in files:
            before.add(
                os.path.join(root, filename)
            )

    cmd = [
        "yt-dlp",
        "-vU",
        "--no-playlist",
        "--no-overwrites",
        "-f",
        "bv*+ba/b",
        "--merge-output-format",
        "mp4",
        "-o",
        output_template,
    ]

    if cookies_from_browser:
        cmd += [
            "--cookies-from-browser",
            cookies_from_browser
        ]

    cmd.append(video_url)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("yt-dlp stdout:\n", result.stdout)
        print("yt-dlp stderr:\n", result.stderr)

        raise RuntimeError(
            "yt-dlp download failed"
        )

    after = set()

    for root, _, files in os.walk(downloads_dir):
        for filename in files:
            after.add(
                os.path.join(root, filename)
            )

    new_files = sorted(after - before)

    mp4_files = [
        path
        for path in new_files
        if (
            path.lower().endswith(".mp4")
            and "_clip_" not in os.path.basename(
                path
            )
        )
    ]

    if mp4_files:
        return mp4_files[0]

    existing = find_latest_nonclip_mp4(
        downloads_dir
    )

    if existing:
        return existing

    raise FileNotFoundError(
        f"No non-clip MP4 file found in: "
        f"{downloads_dir}"
    )


# =========================================================
# 5. DOWNLOAD FULL TWITCH CHAT HTML
# =========================================================

def download_twitch_chat_html(
    video_url,
    output_html_path,
    beginning=None,
    ending=None,
    oauth=None,
    twitchdownloader_cli="TwitchDownloaderCLI",
    reuse_existing=False,
):
    output_dir = os.path.dirname(
        output_html_path
    )

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True
        )

    if (
        reuse_existing
        and os.path.exists(output_html_path)
    ):
        print(
            "Reusing existing chat HTML:",
            output_html_path
        )
        return output_html_path

    vod_id = extract_twitch_vod_id(
        video_url
    )

    cmd = [
        twitchdownloader_cli,
        "chatdownload",
        "--id",
        vod_id,
        "--output",
        output_html_path,
        "--embed-images",
    ]

    if beginning:
        cmd += [
            "--beginning",
            beginning
        ]

    if ending:
        cmd += [
            "--ending",
            ending
        ]

    if oauth:
        cmd += [
            "--oauth",
            oauth
        ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            "TwitchDownloaderCLI stdout:\n",
            result.stdout
        )
        print(
            "TwitchDownloaderCLI stderr:\n",
            result.stderr
        )

        raise RuntimeError(
            "TwitchDownloaderCLI chat download failed"
        )

    if not os.path.exists(output_html_path):
        raise FileNotFoundError(
            f"Chat HTML was not created: "
            f"{output_html_path}"
        )

    return output_html_path


# =========================================================
# 6. EXTRACT WAV FROM VIDEO
# =========================================================

def extract_wav_from_video(
    video_path,
    wav_path,
    reuse_existing=True
):
    if (
        reuse_existing
        and os.path.exists(wav_path)
    ):
        print(
            "Reusing existing WAV:",
            wav_path
        )
        return

    wav_dir = os.path.dirname(wav_path)

    if wav_dir:
        os.makedirs(
            wav_dir,
            exist_ok=True
        )

    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-ac",
        "1",
        "-ar",
        "44100",
        "-sample_fmt",
        "s16",
        wav_path,
        "-y",
    ]

    subprocess.run(
        cmd,
        check=True
    )


# =========================================================
# 7. EXTRACT VIDEO CLIP (OPTIONAL)
# =========================================================

def extract_video_clip(
    video_path,
    output_path,
    start_time,
    end_time,
    reuse_existing=True
):
    if (
        reuse_existing
        and os.path.exists(output_path)
    ):
        print(
            "Reusing existing video clip:",
            output_path
        )
        return

    out_dir = os.path.dirname(output_path)

    if out_dir:
        os.makedirs(
            out_dir,
            exist_ok=True
        )

    cmd = [
        "ffmpeg",
        "-ss",
        start_time,
        "-to",
        end_time,
        "-i",
        video_path,
        "-c",
        "copy",
        output_path,
        "-y",
    ]

    subprocess.run(
        cmd,
        check=True
    )


# =========================================================
# 8. PARSE TWITCH CHAT HTML
# =========================================================

def parse_twitch_comments(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        html_data = file.read()

    soup = BeautifulSoup(
        html_data,
        "html.parser"
    )

    data = []

    for comment in soup.find_all(
        "pre",
        class_="comment-root"
    ):
        raw_text = comment.get_text(
            " ",
            strip=True
        )

        time_str = None

        if (
            raw_text.startswith("[")
            and "]" in raw_text
        ):
            time_str = raw_text.split(
                "]"
            )[0].strip("[")

        badge_img_tag = comment.find(
            "img",
            class_="badge-image"
        )

        badge_img = (
            badge_img_tag["src"]
            if (
                badge_img_tag
                and badge_img_tag.has_attr("src")
            )
            else None
        )

        author_tag = comment.find(
            "span",
            class_="comment-author"
        )

        author = (
            author_tag.get_text(strip=True)
            if author_tag
            else ""
        )

        if badge_img:
            author = (
                f'{author} '
                f'<img src="{badge_img}" width="20">'
            )

        message_tag = comment.find(
            "span",
            class_="comment-message"
        )

        message = (
            message_tag.get_text(
                " ",
                strip=True
            ).lstrip(": ").strip()
            if message_tag
            else ""
        )

        emotes = []

        for emote_tag in comment.find_all(
            "img",
            class_="emote-image"
        ):
            if emote_tag.has_attr("src"):
                emotes.append(
                    f'<img src="{emote_tag["src"]}" '
                    f'width="20">'
                )

        if emotes:
            message = (
                message
                + " "
                + " ".join(emotes)
            ).strip()

        data.append(
            [
                time_str,
                author,
                message
            ]
        )

    df = pd.DataFrame(
        data,
        columns=[
            "time",
            "author",
            "message"
        ]
    )

    df["time"] = df["time"].apply(
        string_to_seconds
    )

    return df


# =========================================================
# 9. TRANSCRIBE FULL AUDIO WITH WHISPERX
# =========================================================

def transcribe_audio_with_whisperx(
    audio_path,
    model_name="small",
    language="fr",
    batch_size=2
):
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    compute_type = "int8"

    model = whisperx.load_model(
        model_name,
        device,
        compute_type=compute_type,
        language=language
    )

    audio = whisperx.load_audio(
        audio_path
    )

    result = model.transcribe(
        audio,
        batch_size=batch_size
    )

    del model
    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    model_a, metadata = (
        whisperx.load_align_model(
            language_code=result["language"],
            device=device
        )
    )

    aligned_result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False
    )

    del model_a
    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    whisper_df = pd.DataFrame(
        aligned_result["segments"]
    )

    if whisper_df.empty:
        return pd.DataFrame(
            columns=["time", "text"]
        )

    whisper_df = whisper_df[
        ["start", "text"]
    ].copy()

    whisper_df.columns = [
        "time",
        "text"
    ]

    whisper_df["time"] = pd.to_numeric(
        whisper_df["time"],
        errors="coerce"
    )

    return whisper_df


# =========================================================
# 10. SAVE / LOAD TRANSCRIPTION CSV
# =========================================================

def save_transcription_csv(df, output_path):
    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )


def load_transcription_csv(path):
    df = pd.read_csv(
        path,
        encoding="utf-8-sig"
    )

    df["time"] = pd.to_numeric(
        df["time"],
        errors="coerce"
    )

    return df


# =========================================================
# 11. MERGE CHAT + SPEECH BY NEAREST TIME
# =========================================================

def merge_chat_and_speech(
    chat_df,
    speech_df,
    tolerance_seconds=2.0
):
    chat_df = chat_df.copy()
    speech_df = speech_df.copy()

    chat_df["time"] = pd.to_numeric(
        chat_df["time"],
        errors="coerce"
    )

    speech_df["time"] = pd.to_numeric(
        speech_df["time"],
        errors="coerce"
    )

    chat_df = (
        chat_df
        .dropna(subset=["time"])
        .sort_values("time")
        .reset_index(drop=True)
    )

    speech_df = (
        speech_df
        .dropna(subset=["time"])
        .sort_values("time")
        .reset_index(drop=True)
    )

    if chat_df.empty:
        return pd.DataFrame(
            columns=[
                "time",
                "author",
                "message",
                "text"
            ]
        )

    if speech_df.empty:
        out = chat_df.copy()
        out["text"] = pd.NA
        return out

    return pd.merge_asof(
        chat_df,
        speech_df,
        on="time",
        direction="nearest",
        tolerance=tolerance_seconds
    )


# =========================================================
# 12. EXPORT HTML TABLE
# =========================================================

def export_html_table(df, output_path):
    df = df.fillna("").copy()
    temp_path = output_path + ".tmp"

    df.to_html(
        temp_path,
        index=False,
        render_links=True,
        escape=False
    )

    with open(
        temp_path,
        "r",
        encoding="utf-8"
    ) as file:
        original_html = file.read()

    html_prefix = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chat and Speech Alignment</title>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
<style>
  body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
  }

  .table-wrapper {
    padding: 20px;
    max-width: 100%;
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #ddd;
    table-layout: fixed;
  }

  th,
  td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
    word-wrap: break-word;
    white-space: normal;
    overflow: hidden;
  }

  th:first-child,
  td:first-child {
    width: 100px;
  }

  th {
    position: sticky;
    top: 0;
    background-color: #343a40;
    color: white;
  }

  tr:nth-child(even) {
    background-color: #f2f2f2;
  }
</style>
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sticky-table-headers/js/jquery.stickytableheaders.min.js"></script>
</head>
<body>
<div class="table-wrapper">
"""

    html_suffix = """
</div>
<script>
  $(document).ready(function() {
    $("table").stickyTableHeaders();
  });
</script>
</body>
</html>
"""

    updated_html = original_html.replace(
        '<table border="1" class="dataframe">',
        '<table border="1" '
        'class="dataframe table table-striped">'
    ).replace(
        '<tr style="text-align: right;">',
        '<tr style="text-align: left;">'
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(
            html_prefix
            + updated_html
            + html_suffix
        )

    os.remove(temp_path)


# =========================================================
# 13. EXPORT CSV
# =========================================================

def export_csv(df, output_path):
    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )


# =========================================================
# 14. PLOT MESSAGE DENSITY
# =========================================================

def plot_message_density(
    merged_df,
    output_png
):
    if merged_df.empty:
        print(
            "Skipping message-density plot: "
            "merged dataframe is empty."
        )
        return

    tmp = merged_df.copy()

    tmp["chat"] = (
        tmp["message"].notna()
        & (tmp["message"] != "")
    )

    tmp["speech"] = (
        tmp["text"].notna()
        & (tmp["text"] != "")
    )

    density_df = (
        tmp.groupby("time")
        .agg(
            chat=("chat", "sum"),
            speech=("speech", "sum")
        )
        .reset_index()
    )

    density_df["minute"] = (
        density_df["time"] / 60
    ).astype(int)

    density_df = (
        density_df
        .groupby("minute")[
            ["chat", "speech"]
        ]
        .sum()
        .reset_index()
    )

    density_long = density_df.melt(
        id_vars="minute",
        value_vars=[
            "chat",
            "speech"
        ],
        var_name="mode",
        value_name="value"
    )

    plt.figure(figsize=(12, 6))

    for mode, group in density_long.groupby(
        "mode"
    ):
        plt.plot(
            group["minute"],
            group["value"],
            label=mode
        )

    ax = plt.gca()

    ax.xaxis.set_major_locator(
        ticker.MultipleLocator(
            1 if HAS_SAMPLE_WINDOW else 5
        )
    )

    ax.xaxis.set_major_formatter(
        ticker.ScalarFormatter()
    )

    plt.xlabel("Time in minutes")
    plt.ylabel("Message Density")
    plt.title("Message Density Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        output_png,
        dpi=600
    )

    plt.close()


# =========================================================
# 15. PSEUDONYMISE HTML OUTPUT
# =========================================================

def anonymize_html(
    file_path,
    output_path
):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        soup = BeautifulSoup(
            file,
            "html.parser"
        )

    moderator_badge = (
        "https://static-cdn.jtvnw.net/badges/v1/"
        "3267646d-33f0-4b17-b3df-f923a41db1d0/2"
    )

    broadcaster_badge = (
        "https://static-cdn.jtvnw.net/badges/v1/"
        "5527c58c-fb7d-422d-b71b-f309dcb85cc1/2"
    )

    user_mapping = {}
    moderator_counter = 1
    user_counter = 1

    rows = soup.find_all("tr")[1:]

    for row in rows:
        columns = row.find_all("td")

        if len(columns) < 3:
            continue

        author_td = columns[1]
        message_td = (
            columns[2]
            if len(columns) > 2
            else None
        )

        author_text = author_td.get_text(
            strip=True
        )

        author_lower = author_text.lower()

        role = "User"
        img_tag = author_td.find("img")

        if (
            img_tag
            and img_tag.has_attr("src")
        ):
            badge_url = img_tag["src"]

            if badge_url == broadcaster_badge:
                role = "Broadcaster"
            elif badge_url == moderator_badge:
                role = "Moderator"

        if (
            author_lower
            and author_lower not in user_mapping
        ):
            if role == "Broadcaster":
                user_mapping[
                    author_lower
                ] = "Broadcaster"

            elif role == "Moderator":
                user_mapping[
                    author_lower
                ] = (
                    f"Moderator"
                    f"{moderator_counter}"
                )
                moderator_counter += 1

            else:
                user_mapping[
                    author_lower
                ] = f"User{user_counter}"
                user_counter += 1

        if author_lower in user_mapping:
            author_td.clear()
            author_td.string = user_mapping[
                author_lower
            ]

        if (
            message_td is not None
            and user_mapping
        ):
            pattern = re.compile(
                r"@("
                + "|".join(
                    re.escape(name)
                    for name in user_mapping.keys()
                )
                + r")",
                flags=re.IGNORECASE
            )

            def replace_tag(match):
                name = match.group(1).lower()

                return (
                    f"@"
                    f"{user_mapping.get(name, name)}"
                )

            message_html = (
                message_td.decode_contents()
            )

            updated_message = pattern.sub(
                replace_tag,
                message_html
            )

            message_td.clear()

            message_td.append(
                BeautifulSoup(
                    updated_message,
                    "html.parser"
                )
            )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(str(soup))

    print("Pseudonymisation completed.")


# =========================================================
# 16. MAIN WORKFLOW
# =========================================================

def main():
    ensure_command_exists("yt-dlp")
    ensure_command_exists("ffmpeg")
    ensure_command_exists("ffprobe")
    ensure_command_exists(
        TWITCHDOWNLOADER_CLI
    )

    # Retrieve metadata and create an isolated folder
    # for the current Twitch VOD
    video_directories = create_video_directories(
        VIDEO_URL,
        cookies_from_browser=(
            TWITCH_COOKIES_FROM_BROWSER
        )
    )

    metadata = video_directories[
        "metadata"
    ]

    video_root_dir = video_directories[
        "video_root_dir"
    ]

    downloads_dir = video_directories[
        "downloads_dir"
    ]

    chat_dir = video_directories[
        "chat_dir"
    ]

    output_dir = video_directories[
        "output_dir"
    ]

    print("Twitch VOD ID:", metadata["id"])
    print("Twitch title:", metadata["title"])
    print("VOD archive folder:", video_root_dir)

    # Video filename also includes the VOD ID
    ytdlp_output_template = os.path.join(
        downloads_dir,
        "%(title)s [%(id)s].%(ext)s"
    )

    full_chat_html_path = os.path.join(
        chat_dir,
        FULL_CHAT_HTML_NAME
    )

    merged_html_path = os.path.join(
        output_dir,
        MERGED_HTML_NAME
    )

    pseudonymised_html_path = os.path.join(
        output_dir,
        MERGED_HTML_PSEUDONYMIZED_NAME
    )

    merged_csv_path = os.path.join(
        output_dir,
        MERGED_CSV_NAME
    )

    density_png_path = os.path.join(
        output_dir,
        DENSITY_PNG_NAME
    )

    full_chat_csv_path = os.path.join(
        output_dir,
        FULL_CHAT_CSV_NAME
    )

    full_transcription_csv_path = os.path.join(
        output_dir,
        FULL_TRANSCRIPTION_CSV_NAME
    )

    full_merged_csv_path = os.path.join(
        output_dir,
        FULL_MERGED_CSV_NAME
    )

    print_versions()

    # -----------------------------------------------------
    # 1) Download full video
    # -----------------------------------------------------
    full_video_path = download_twitch_video(
        VIDEO_URL,
        ytdlp_output_template,
        downloads_dir=downloads_dir,
        cookies_from_browser=(
            TWITCH_COOKIES_FROM_BROWSER
        )
    )

    print(
        "Full video downloaded:",
        full_video_path
    )

    # -----------------------------------------------------
    # 2) Optional video clip extraction
    # -----------------------------------------------------
    if (
        HAS_SAMPLE_WINDOW
        and EXTRACT_VIDEO_CLIP
    ):
        clip_video_path = (
            os.path.splitext(
                full_video_path
            )[0]
            + f"_clip_{SAMPLE_SUFFIX}.mp4"
        )

        extract_video_clip(
            full_video_path,
            clip_video_path,
            SAMPLE_START,
            SAMPLE_END,
            reuse_existing=(
                REUSE_EXISTING_VIDEO_CLIP
            )
        )

        print(
            "Clip video created:",
            clip_video_path
        )

    # -----------------------------------------------------
    # 3) Full WAV extraction
    # -----------------------------------------------------
    full_wav_path = (
        os.path.splitext(
            full_video_path
        )[0]
        + ".wav"
    )

    extract_wav_from_video(
        full_video_path,
        full_wav_path,
        reuse_existing=(
            REUSE_EXISTING_FULL_WAV
        )
    )

    print(
        "Full WAV file created:",
        full_wav_path
    )

    # -----------------------------------------------------
    # 4) Download full chat HTML
    # -----------------------------------------------------
    download_twitch_chat_html(
        VIDEO_URL,
        full_chat_html_path,
        oauth=TWITCHDOWNLOADER_OAUTH,
        twitchdownloader_cli=(
            TWITCHDOWNLOADER_CLI
        ),
        reuse_existing=(
            REUSE_EXISTING_FULL_CHAT_HTML
        ),
    )

    print(
        "Full chat HTML created:",
        full_chat_html_path
    )

    # -----------------------------------------------------
    # 5) Parse full chat
    # -----------------------------------------------------
    full_chat_df = parse_twitch_comments(
        full_chat_html_path
    )

    if not full_chat_df.empty:
        print(
            "Full chat time min/max:",
            full_chat_df["time"].min(),
            full_chat_df["time"].max()
        )
    else:
        print(
            "Full chat dataframe is empty."
        )

    print(
        "Full chat rows:",
        len(full_chat_df)
    )

    export_csv(
        full_chat_df,
        full_chat_csv_path
    )

    print(
        "Saved full chat CSV to:",
        full_chat_csv_path
    )

    # -----------------------------------------------------
    # 6) Full transcription
    # -----------------------------------------------------
    if (
        REUSE_EXISTING_FULL_TRANSCRIPTION_CSV
        and os.path.exists(
            full_transcription_csv_path
        )
    ):
        full_whisper_df = (
            load_transcription_csv(
                full_transcription_csv_path
            )
        )

        print(
            "Loaded existing full "
            "transcription CSV:",
            full_transcription_csv_path
        )
    else:
        full_whisper_df = (
            transcribe_audio_with_whisperx(
                full_wav_path,
                model_name=WHISPER_MODEL,
                language=LANGUAGE,
                batch_size=BATCH_SIZE
            )
        )

        save_transcription_csv(
            full_whisper_df,
            full_transcription_csv_path
        )

        print(
            "Saved full transcription CSV to:",
            full_transcription_csv_path
        )

    if not full_whisper_df.empty:
        print(
            "Full speech time min/max:",
            full_whisper_df["time"].min(),
            full_whisper_df["time"].max()
        )
    else:
        print(
            "Full speech dataframe is empty."
        )

    print(
        "Full speech segments:",
        len(full_whisper_df)
    )

    # -----------------------------------------------------
    # 7) Full merged CSV
    # -----------------------------------------------------
    full_merged_df = merge_chat_and_speech(
        full_chat_df,
        full_whisper_df,
        tolerance_seconds=(
            MERGE_TOLERANCE_SECONDS
        )
    )

    print(
        "Full merged rows:",
        len(full_merged_df)
    )

    export_csv(
        full_merged_df,
        full_merged_csv_path
    )

    print(
        "Saved full merged CSV to:",
        full_merged_csv_path
    )

    # -----------------------------------------------------
    # 8) Extract sample from full data
    # -----------------------------------------------------
    if HAS_SAMPLE_WINDOW:
        sample_chat_df = (
            filter_df_by_time_window(
                full_chat_df,
                SAMPLE_START,
                SAMPLE_END,
                rebase_to_zero=True
            )
        )

        sample_whisper_df = (
            filter_df_by_time_window(
                full_whisper_df,
                SAMPLE_START,
                SAMPLE_END,
                rebase_to_zero=True
            )
        )
    else:
        sample_chat_df = (
            full_chat_df.copy()
        )

        sample_whisper_df = (
            full_whisper_df.copy()
        )

    if not sample_chat_df.empty:
        print(
            "Sample chat time min/max:",
            sample_chat_df["time"].min(),
            sample_chat_df["time"].max()
        )
    else:
        print(
            "Sample chat dataframe is empty."
        )

    print(
        "Sample chat rows:",
        len(sample_chat_df)
    )

    if not sample_whisper_df.empty:
        print(
            "Sample speech time min/max:",
            sample_whisper_df["time"].min(),
            sample_whisper_df["time"].max()
        )
    else:
        print(
            "Sample speech dataframe is empty."
        )

    print(
        "Sample speech segments:",
        len(sample_whisper_df)
    )

    # -----------------------------------------------------
    # 9) Merge sample
    # -----------------------------------------------------
    merged_df = merge_chat_and_speech(
        sample_chat_df,
        sample_whisper_df,
        tolerance_seconds=(
            MERGE_TOLERANCE_SECONDS
        )
    )

    print(
        "Merged rows:",
        len(merged_df)
    )

    # -----------------------------------------------------
    # 10) Export sampled outputs
    # -----------------------------------------------------
    export_html_table(
        merged_df,
        merged_html_path
    )

    print(
        "Saved HTML to:",
        merged_html_path
    )

    export_csv(
        merged_df,
        merged_csv_path
    )

    print(
        "Saved CSV to:",
        merged_csv_path
    )

    plot_message_density(
        merged_df,
        density_png_path
    )

    if os.path.exists(density_png_path):
        print(
            "Saved plot to:",
            density_png_path
        )

    anonymize_html(
        merged_html_path,
        pseudonymised_html_path
    )

    print(
        "Saved pseudonymised HTML to:",
        pseudonymised_html_path
    )

    print("\nWorkflow completed.")
    print("All files are stored in:")
    print(video_root_dir)


if __name__ == "__main__":
    main()
