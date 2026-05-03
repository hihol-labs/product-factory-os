# Voice To Text Integration

Product Factory OS supports a pluggable local voice-to-text adapter:

```bash
python3 scripts/voice_transcribe.py command.wav
```

The adapter uses a local Whisper-compatible CLI when available. The transcript should then be passed to:

```bash
python3 scripts/pfo.py voice "transcribed command"
```

This keeps voice-first operation independent from any single cloud provider.

