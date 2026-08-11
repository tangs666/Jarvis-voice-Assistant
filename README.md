# Jarvis-Voice-Assistant

基于 Ollama (Qwen2.5) 与 Vosk 开发的本地轻量级 AI 语音助手，集成 PyQt6 动态波形界面、**毫秒级语音打断**与**空格键物理打断**机制。

---

## ✨ 核心特性

* **毫秒级双重打断**：说出“停下”、“暂停”、“等一下”等词汇，或按键盘 **`Space`（空格键）** 瞬间拉闸切断播报。
* **完全本地运行**：依托 Ollama 本地大语言模型，数据绝不出户，零网络依赖。
* **可视化动态 UI**：基于 PyQt6 实现的声音波形界面，随说话音量实时动态变化。
* **全平台自适应**：无缝兼容 Windows、macOS 和 Linux。

---

## 🛠️ 环境准备与详细配置

### 1. 运行环境要求
* **Python 3.9 或以上**
* 必须先安装并启动 [Ollama](https://ollama.com/)

### 2. 下载并启动本地大模型
根据你的电脑配置选择拉取合适的模型：

* **基础配置 / 轻量设备**：
  ```bash
  ollama run qwen2.5:1.5b
  ```
* **高配设备 / 追求更好回答质量**（内存 16G+）：
  ```bash
  ollama run qwen2.5:7b
  ```
> 💡 *若使用 7B 模型，只需打开 `jarvis_gui.py` 将模型名称改为 `qwen2.5:7b` 即可。*

### 3. 下载 Vosk 语音识别模型（跨平台通用）
1. 前往 [Vosk 官方模型下载页](https://alphacephei.com/vosk/models) 下载中文轻量模型：`vosk-model-small-cn-0.22`。
2. 将下载好的压缩包解压后，重命名文件夹为 `model`，并直接放入**项目根目录**下。

**标准目录结构**：
```text
Jarvis-voice-Assistant/
├── jarvis_gui.py
├── model/               <-- Vosk 语音模型文件夹（里面包含 am, conf 等子文件夹）
└── README.md
```

### 4. 安装 Python 依赖包（多系统适配）

根据你的操作系统执行对应命令：

#### 🔹 Windows 系统：
```bash
pip install PyQt6 vosk pygame pyaudio numpy requests edge-tts
```
*(若安装 `pyaudio` 报错，请先执行 `pip install pipwin`，再执行 `pipwin install pyaudio`)*

#### 🔹 macOS 系统：
```bash
brew install portaudio
pip install PyQt6 vosk pygame pyaudio numpy requests edge-tts
```

#### 🔹 Linux 系统 (Ubuntu/Debian)：
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install PyQt6 vosk pygame pyaudio numpy requests edge-tts
```

---

## 🚀 运行与使用说明

1. 确保后台已启动 Ollama 服务。
2. 在项目根目录下打开终端，运行启动命令：
   ```bash
   python jarvis_gui.py
   ```
3. **快捷打断操作**：
   * **语音打断**：AI 在回答播报时，直接对麦克风喊“停一下”、“暂停”或“安静”。
   * **按键打断**：按下键盘 **`Space`（空格键）** 随时强行终止播报。

---
## 🗺️ 未来规划 (Roadmap) & 欢迎贡献

* [ ] 支持自定义唤醒词（Wake Word）
* [ ] 增加更多 UI 主题与波形样式
* [ ] 支持本地历史对话记忆导出

如果你有好的想法或发现了 Bug，非常欢迎提交 **Issue** 或 **Pull Request** 参与建设！
如果你喜欢这个项目，请点一个 **Star 🌟** 支持一下
## 📄 开源协议与版权声明

本项目基于 **[GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.html)** 协议开源。

* **自由使用与修改**：欢迎个人学习、研究以及开源社区的二次开发与交流。
* **开源传染性**：任何基于本项目二次修改、衍生或引用的代码，**必须同样以 GPL-3.0 协议开源**，不得直接打包为商业闭源软件。
* **商业授权**：若需在不遵循 GPL-3.0 开源条约的情况下进行商业化使用、变相盈利或打包销售，**必须事先取得作者的书面授权**。
