# Jarvis-Voice-Assistant

这是一个基于 Ollama 和 Vosk 开发的本地轻量级 AI 语音助手，具备**极速语音打断**与**物理按键响应**机制，让交互更加自然顺畅。

## ✨ 核心亮点

* **毫秒级语音打断**：内置流式语音识别，说出“停一下”、“暂停”等关键词可立即打断 AI 播报。
* **物理空格秒停**：按下键盘空格键（Space）瞬间强行拉闸切断音频，0 延迟响应。
* **本地隐私安全**：基于 Ollama 运行本地大语言模型（默认 Qwen2.5），无需联网，数据绝不出户。
* **可视化波形 UI**：基于 PyQt6 实现的动态波形界面，根据说话音量实时响应。
* **对话持久化**：自动保存角色设定与历史上下文记忆。

## 🚀 快速开始

### 1. 准备环境
* 安装 [Ollama](https://ollama.com/) 并拉取模型：
  ```bash
  ollama run qwen2.5:1.5b
vosk-model-small-cn-0.22
pip install vosk PyQt6 pygame pyaudio numpy requests edge-tts
python jarvis_gui.py
