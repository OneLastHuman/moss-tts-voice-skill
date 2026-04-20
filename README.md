# MOSS-TTS-Voice Skill

A Claude Code skill for generating voice cloning TTS audio using [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano).

## What it does

Given a reference audio clip and text, generates a cloned voice speech audio file. Converts to OPUS format and sends via file link.

## Requirements

- Python 3.13
- `/usr/local/bin/python3.13` (Intel Mac compatible)
- Dependencies: `onnxruntime`, `soundfile`, `sentencepiece`, `scipy`
- `ffmpeg` (for OPUS conversion)

### Install dependencies

```bash
/usr/local/bin/python3.13 -m pip install onnxruntime soundfile sentencepiece scipy --break-system-packages
```

## Usage

When you ask for a voice message or TTS generation, the skill:
1. Generates a WAV using the reference audio as voice clone source
2. Converts to OPUS via ffmpeg
3. Sends the file to you

## Model

Uses the ONNX CPU model from [OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX](https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX):
- 0.1B parameters, fully CPU inference (~2-3s per generation)
- No GPU, no PyTorch required
- 20 languages supported

## Files

```
moss-tts-voice/
├── SKILL.md                    # Claude Code skill definition
└── scripts/
    ├── infer.py                # TTS inference entrypoint
    └── ort_cpu_runtime.py      # ONNX CPU runtime (from MOSS-TTS-Nano)
```

## Reference Audios

Bundled reference clips (from MOSS-TTS-Nano project):

| Path | Language |
|------|----------|
| `assets/audio/zh_1.wav` | Chinese (female) |
| `assets/audio/zh_3.wav` | Chinese (male) |
| `assets/audio/en_2.wav` | English |
| `assets/audio/jp_2.wav` | Japanese |

Or provide your own reference audio path.

## License

Apache 2.0 — same as [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano).
