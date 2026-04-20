#!/usr/bin/env python3
"""Minimal ONNX CPU voice cloning TTS — no PyTorch/torchaudio."""

import wave
import numpy as np
import soundfile as sf
import sentencepiece as spm
from scipy.signal import resample_poly
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ort_cpu_runtime import OrtCpuRuntime


MODEL_DIR = Path.home() / ".cache" / "moss_tts_nano" / "models"


def download_models(model_dir: Path) -> None:
    from huggingface_hub import snapshot_download
    (model_dir / "MOSS-TTS-Nano-100M-ONNX").mkdir(parents=True, exist_ok=True)
    (model_dir / "MOSS-Audio-Tokenizer-Nano-ONNX").mkdir(parents=True, exist_ok=True)
    print("Downloading TTS model...")
    snapshot_download(repo_id="OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX",
        local_dir=str(model_dir / "MOSS-TTS-Nano-100M-ONNX"),
        local_dir_use_symlinks=False,
        allow_patterns=["*.onnx", "*.data", "*.json", "tokenizer.model"])
    print("Downloading Codec model...")
    snapshot_download(repo_id="OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX",
        local_dir=str(model_dir / "MOSS-Audio-Tokenizer-Nano-ONNX"),
        local_dir_use_symlinks=False,
        allow_patterns=["*.onnx", "*.data", "*.json"])


def ensure_models(model_dir: Path) -> Path:
    # Check in subdirectory where OrtCpuRuntime looks
    if not (model_dir / "MOSS-TTS-Nano-100M-ONNX" / "browser_poc_manifest.json").exists():
        print("Models missing, downloading...")
        download_models(model_dir)
    return model_dir


def load_audio(path: str | Path, target_sr: int, target_ch: int) -> np.ndarray:
    audio, sr = sf.read(str(path), dtype='float32')
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=1)
    if sr != target_sr:
        audio = resample_poly(audio, target_sr, sr, axis=0)
    if audio.shape[1] != target_ch:
        audio = audio[:, :target_ch] if audio.shape[1] > target_ch else np.repeat(audio, target_ch, axis=1)
    return audio.T.astype(np.float32)


def run_tts(prompt_audio: str, text: str, output_path: str, threads: int = 4) -> str:
    """Returns path to generated WAV file."""
    model_dir = ensure_models(MODEL_DIR)
    rt = OrtCpuRuntime(model_dir=model_dir, thread_count=threads)

    tokenizer_path = rt.resolve_manifest_relative_path(rt.manifest["model_files"]["tokenizer_model"])
    sp = spm.SentencePieceProcessor(model_file=str(tokenizer_path))

    codec_meta = rt.codec_meta
    sr = int(codec_meta["codec_config"]["sample_rate"])
    n_ch = int(codec_meta["codec_config"]["channels"])
    n_vq = int(codec_meta["codec_config"]["num_quantizers"])

    waveform = load_audio(prompt_audio, sr, n_ch)
    wb = waveform[np.newaxis, :, :]
    out = rt.sessions["codec_encode"].run(None, {
        "waveform": wb.astype(np.float32),
        "input_lengths": np.array([waveform.shape[1]], dtype=np.int32)
    })
    names = [o.name for o in rt.sessions["codec_encode"].get_outputs()]
    named = dict(zip(names, out))
    codes = np.asarray(named["audio_codes"], dtype=np.int32)
    lengths = np.asarray(named["audio_code_lengths"], dtype=np.int32)
    code_len = int(lengths.reshape(-1)[0])
    prompt_codes = [[int(codes[0, i, q]) for q in range(n_vq)] for i in range(code_len)]

    text = text.strip()
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        if text[-1] not in '。！？':
            text += '。'
    elif text[-1].isalnum():
        text += '.'
    tokens = [int(t) for t in sp.encode(text, out_type=int)]

    rows = rt.build_voice_clone_request_rows(prompt_codes, tokens)
    frames = rt.generate_audio_frames(rows)

    ch_arrays, _ = rt.decode_full_audio(frames)
    min_len = min(a.shape[0] for a in ch_arrays)
    audio = np.stack([a[:min_len] for a in ch_arrays], axis=1)

    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(n_ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    return output_path


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--output", default="/Users/hue/Desktop/output.wav")
    p.add_argument("--threads", type=int, default=4)
    args = p.parse_args()
    result = run_tts(args.prompt, args.text, args.output, args.threads)
    print(f"Saved: {result}")
