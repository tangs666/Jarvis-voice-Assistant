# 🤖 J.A.R.V.I.S. HUD Terminal (v2.0)

基于 Ollama 大语言模型与 PyQt6 开发的离线轻量级 AI 语音助手，集成钢铁侠 HUD 极客控制台与全流程语音交互。

---

## ✨ 核心特性

* **HUD 极客视觉**：深色发光 UI，`QPainter` 逐帧绘制动态旋转 AI 核心。
* **全流程语音闭环**：支持麦克风语音输入、Ollama 推理与 pyttsx3 离线语音朗读。
* **多线程防卡死**：采用 `QThread` 架构，AI 思考时界面依旧保持流畅。

---

## 🛠️ 环境准备与配置

1. 安装依赖包：
```bash
pip install PyQt6 requests speechrecognition pyttsx3 pyaudio
ollama run llama3
python v2/jarvis_gui_v2.py
