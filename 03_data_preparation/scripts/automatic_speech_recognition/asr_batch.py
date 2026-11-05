#!/usr/bin/env python3
"""
(step1) In Terminal
Install faster-whisper
pip3 install faster-whisper

After installation, verify:
python3 -c "from faster_whisper import WhisperModel; print('OK')"

(step2)
In the same directory where asr_batch.py is saved, create a folder entitled "audio_in" then place your input audio files inside

(step3)Run transcription in Terminal:
Italian speech recognition
python3 asr_batch.py ./audio_in ./out --engine whisper --model medium --language it --formats txt,json

French speech recognition
python3 asr_batch.py ./audio_in ./out --engine whisper --model medium --language fr --formats txt,json

Word-level timestamps
python3 asr_batch.py ./audio_in ./out --engine whisperx --model large-v2 --language fr --formats txt,json,words

You may see:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
This is normal. It occurs during model download from Hugging Face. It's not necessary to set a HF_TOKEN (https://huggingface.co/pricing).
The script will run without authentification and the first download may take some time.

%%Batch ASR for FR/IT with:
- Engine "whisper"  : faster-whisper (fast, strong accuracy, segment timestamps)
- Engine "whisperx" : whisperx (alignment -> word timestamps)

%%Outputs per file:
- .txt  (full text)
- .json (segments + metadata)
- .words.json (word-level timestamps)  [only when available]
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

AUDIO_EXTS = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".mp4", ".mpeg", ".aac", ".amr"}

def list_media(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]
    files = [p for p in input_path.rglob("*") if p.suffix.lower() in AUDIO_EXTS]
    return sorted(files)

def safe_stem(path: Path) -> str:
    # Keep original stem; adjust here if you want custom naming rules
    return path.stem

def write_text(out_txt: Path, segments: List[Dict[str, Any]]) -> None:
    text = " ".join(s["text"].strip() for s in segments).strip()
    out_txt.write_text(text + ("\n" if text else ""), encoding="utf-8")

def write_json(out_json: Path, payload: Dict[str, Any]) -> None:
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def run_faster_whisper(
    media_path: Path,
    model_size: str,
    device: str,
    compute_type: str,
    language: Optional[str],
    vad_filter: bool,
) -> Dict[str, Any]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    segments_iter, info = model.transcribe(
        str(media_path),
        language=language,          # "fr" or "it" or None (= auto)
        vad_filter=vad_filter,
    )

    segments: List[Dict[str, Any]] = []
    for s in segments_iter:
        segments.append({
            "id": getattr(s, "id", None),
            "start": float(s.start),
            "end": float(s.end),
            "text": s.text,
        })

    return {
        "engine": "faster-whisper",
        "model": model_size,
        "detected_language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
        "segments": segments,
        # Note: faster-whisper gives segment timestamps; word timestamps are not the default here.
    }

def run_whisperx(
    media_path: Path,
    model_size: str,
    device: str,
    compute_type: str,
    language: Optional[str],
    vad_filter: bool,
) -> Dict[str, Any]:
    """
    WhisperX does:
    1) Whisper transcription (segments)
    2) Alignment => word-level timestamps (when alignment model available)
    """
    import whisperx

    # 1) ASR
    asr_model = whisperx.load_model(model_size, device=device, compute_type=compute_type, language=language)
    result = asr_model.transcribe(str(media_path), vad_filter=vad_filter)

    # 2) Alignment (word timestamps)
    # If language was None (auto), whisperx returns language in result["language"]
    lang = result.get("language", language)
    align_model, metadata = whisperx.load_align_model(language_code=lang, device=device)
    aligned = whisperx.align(result["segments"], align_model, metadata, str(media_path), device=device)

    # Normalize output (segments + words if present)
    segments_out: List[Dict[str, Any]] = []
    words_out: List[Dict[str, Any]] = []

    for seg in aligned.get("segments", []):
        segments_out.append({
            "start": float(seg.get("start", 0.0)),
            "end": float(seg.get("end", 0.0)),
            "text": seg.get("text", ""),
        })
        for w in seg.get("words", []) or []:
            # whisperx commonly uses keys: word/start/end/score
            if "start" in w and "end" in w:
                words_out.append({
                    "word": w.get("word", ""),
                    "start": float(w["start"]),
                    "end": float(w["end"]),
                    "score": w.get("score", None),
                })

    payload = {
        "engine": "whisperx",
        "model": model_size,
        "language": lang,
        "segments": segments_out,
    }
    if words_out:
        payload["words"] = words_out

    return payload

def main() -> None:
    p = argparse.ArgumentParser(
        description="Batch ASR (FR/IT) with TXT/JSON + optional word timestamps",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("input", type=Path, help="Input file or folder")
    p.add_argument("output_dir", type=Path, help="Output directory")
    p.add_argument("--engine", choices=["whisper", "whisperx"], default="whisper",
                   help="ASR engine: whisper=faster-whisper; whisperx=alignment word timestamps")
    p.add_argument("--model", default="medium", help="Model size (e.g., small/medium/large-v2/large-v3)")
    p.add_argument("--language", choices=["fr", "it"], default=None, help="Force language or auto-detect")
    p.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Device (MacBook Air => cpu)")
    p.add_argument("--compute_type", default="int8", help="e.g., int8 for CPU")
    p.add_argument("--vad_filter", action="store_true", help="Enable VAD filtering (often improves noisy files)")
    p.add_argument("--formats", default="txt,json,words",
                   help="Comma-separated outputs: txt,json,words. 'words' requires whisperx (or will be skipped).")

    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    formats = {f.strip().lower() for f in args.formats.split(",") if f.strip()}
    files = list_media(args.input)
    if not files:
        raise SystemExit(f"No media found in {args.input.resolve()}")

    for media in files:
        base = args.output_dir / safe_stem(media)

        if args.engine == "whisper":
            payload = run_faster_whisper(
                media, args.model, args.device, args.compute_type, args.language, args.vad_filter
            )
            segments = payload["segments"]

            if "txt" in formats:
                write_text(base.with_suffix(".txt"), segments)
            if "json" in formats:
                write_json(base.with_suffix(".json"), payload)
            if "words" in formats:
                # faster-whisper mode: no word timestamps by default
                # You can add a second pass with whisperx if you need word-level.
                pass

        else:  # whisperx
            payload = run_whisperx(
                media, args.model, args.device, args.compute_type, args.language, args.vad_filter
            )
            segments = payload.get("segments", [])

            if "txt" in formats:
                write_text(base.with_suffix(".txt"), segments)
            if "json" in formats:
                write_json(base.with_suffix(".json"), payload)
            if "words" in formats:
                words = payload.get("words", [])
                if words:
                    write_json(base.with_suffix(".words.json"), {"words": words})
                # If no words, we silently skip (alignment may fail depending on setup)

    print(f"Done. Outputs in: {args.output_dir.resolve()}")

if __name__ == "__main__":
    main()
