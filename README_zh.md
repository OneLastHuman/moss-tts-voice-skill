# MOSS-TTS-Voice 技能

基于 [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano) 的 Claude Code 语音克隆 TTS 生成技能。

## 功能简介

只需提供一段参考音频和文本，即可生成克隆音色的语音消息。生成的音频会转换为 OPUS 格式，并以文件链接形式发送。

## 环境要求

- Python 3.13
- `/usr/local/bin/python3.13`（兼容 Intel Mac）
- 依赖包：`onnxruntime`, `soundfile`, `sentencepiece`, `scipy`
- `ffmpeg`（用于 OPUS 转码）

### 安装依赖

```bash
/usr/local/bin/python3.13 -m pip install onnxruntime soundfile sentencepiece scipy --break-system-packages
```

## 使用方法

当请求语音消息或 TTS 生成时，技能会：
1. 使用参考音频进行声音克隆，生成 WAV 格式语音
2. 用 ffmpeg 转为 OPUS 格式
3. 通过文件链接返回给你

## 模型说明

使用 [OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX](https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX) 中的 ONNX CPU 推理模型：
- 0.1B 参数，纯 CPU 运行（每次约 2-3 秒）
- 无需 GPU 或 PyTorch 环境
- 支持 20 种语言

## 文件结构

```
moss-tts-voice/
├── SKILL.md                    # Claude Code 技能定义文件
└── scripts/
    ├── infer.py                # TTS 推理主程序
    └── ort_cpu_runtime.py      # ONNX CPU 推理库（来自 MOSS-TTS-Nano）
```

## 参考音频

内置 MOSS-TTS-Nano 的参考音频片段：

| 路径 | 语言 |
|------|------|
| `assets/audio/zh_1.wav` | 中文（女声）|
| `assets/audio/zh_3.wav` | 中文（男声）|
| `assets/audio/en_2.wav` | 英文 |
| `assets/audio/jp_2.wav` | 日文 |

你也可以自行提供参考音频路径。

## 许可证

Apache 2.0 — 与 [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano) 保持一致。