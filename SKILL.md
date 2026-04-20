---
name: moss-tts-voice
description: MOSS-TTS-Nano voice cloning TTS generator. Use when the user asks to generate, synthesize, or clone a voice, make TTS audio, or send a voice message. Generates a voice cloning TTS audio from a reference audio clip and text, converts to OPUS, and sends the file. Supports Chinese, English, Japanese, and 17 other languages. Requires Python 3.13 with onnxruntime, soundfile, sentencepiece, scipy installed.
---

## Workflow

1. **Determine reference audio and text**
   - Reference audio: use `assets/audio/zh_1.wav` for Chinese, `assets/audio/en_2.wav` for English, `assets/audio/jp_2.wav` for Japanese. Or accept any local audio path the user provides.
   - Text: what the user wants to say.

2. **Generate WAV**
   ```bash
   /usr/local/bin/python3.13 /Users/hue/.ductor/workspace/skills/moss-tts-voice/scripts/infer.py \
     --prompt /path/to/reference.wav \
     --text "用户文本" \
     --output /tmp/tts_output.wav
   ```
   Model downloads automatically on first run (~100MB ONNX files cached to `~/.cache/moss_tts_nano/models/`).

3. **Convert to OPUS**
   ```bash
   ffmpeg -i /tmp/tts_output.wav -c:a libopus -b:a 128k /tmp/tts_output.opus -y
   ```

4. **Send file to user**
   Send the message: `<file:/tmp/tts_output.opus>`

## Supported Languages
Chinese, English, Japanese, Korean, German, French, Spanish, Italian, Portuguese, Russian, Arabic, Hindi, Vietnamese, Thai, Indonesian, Malay, Turkish, Polish, Dutch, Ukrainian.

## Reference Audio Paths
- `/Users/hue/Documents/MOSS-TTS-Nano/assets/audio/zh_1.wav` — Chinese female
- `/Users/hue/Documents/MOSS-TTS-Nano/assets/audio/zh_3.wav` — Chinese
- `/Users/hue/Documents/MOSS-TTS-Nano/assets/audio/en_2.wav` — English
- `/Users/hue/Documents/MOSS-TTS-Nano/assets/audio/jp_2.wav` — Japanese

## Notes
- Generation: ~2-3s on CPU (no GPU needed, no PyTorch)
- Output: 48kHz stereo WAV → OPUS 128kbps
- If user provides a custom reference audio, use their path directly
- Text is auto-normalized (Chinese adds "。" if missing, English adds ".")
