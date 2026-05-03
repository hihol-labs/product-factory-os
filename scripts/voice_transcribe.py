#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe audio into text for Product Factory OS voice commands.")
    parser.add_argument("audio", type=Path)
    parser.add_argument("--language", default="ru")
    args = parser.parse_args()

    if not args.audio.is_file():
        raise SystemExit(f"ERROR: missing audio file: {args.audio}")

    whisper = shutil.which("whisper")
    if whisper:
        result = subprocess.run(
            [whisper, str(args.audio), "--language", args.language, "--model", "base", "--output_format", "txt"],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            raise SystemExit(result.stdout + result.stderr)
        print(result.stdout.strip())
        return

    raise SystemExit(
        "ERROR: no local speech-to-text engine found. Install OpenAI Whisper CLI or faster-whisper, "
        "then pipe the transcript into `python3 scripts/pfo.py voice \"...\"`."
    )


if __name__ == "__main__":
    main()

