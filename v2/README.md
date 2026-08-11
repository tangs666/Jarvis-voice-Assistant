# 🤖 J.A.R.V.I.S. HUD Terminal (v2.0.0)

欢迎来到 J.A.R.V.I.S. v2.0 专属页面！本版本将系统的视觉交互与后端逻辑进行了全面升级，打造了一个具有**钢铁侠 HUD 科技感**且支持**离线语音交互闭环**的完整 AI 控制台。

---

## ✨ v2.0 独家核心特性

* **HUD 极客视觉**：全深色背景搭配青色发光组件，采用 PyQt6 `QPainter` 逐帧绘制双向旋转 AI 动画核心。
* **语音/大模型/TTS 闭环**：
  * **输入**：集成 `SpeechRecognition` 实时采集麦克风语音并转换为文本。
  * **大脑**：通过 HTTP 接口无缝连接本地 `Ollama` 大语言模型进行推理。
  * **输出**：使用 `pyttsx3` 将 AI 的回复实时进行语音朗读。
* **异步多线程 (QThread)**：采用多线程架构，语音识别、AI 思考与声音播报不会阻塞 UI 主线程，核心动画持续流畅运行。
* **实时系统日志**：右侧滚动展示通信脉冲、状态心跳与对话日志。

---

## 🛠️ 环境准备与依赖安装

请确保系统已安装 Python 3.9+，并在终端运行以下命令安装所需依赖库：

```bash
pip install PyQt6 requests speechrecognition pyttsx3 pyaudio
python v2/jarvis_gui_v2.py
拉到最下方，点击 **`Commit changes...`** 保存。

---

**第二步：确认 `v2/jarvis_gui_v2.py` 完整代码**

请确保你的 `v2/jarvis_gui_v2.py` 文件中内容与以下**完整代码**一致：

```python
import sys
import random
import threading
import requests
import speech_recognition as sr
import pyttsx3
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- 离线语音合成引擎 ---
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- 核心大脑线程：连接 Ollama 并播报 ---
class JarvisBrain(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            self.log_signal.emit(f"AI 正在思考: {self.prompt}...")
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3", 
                "prompt": self.prompt,
                "stream": False
            })
            if response.status_code == 200:
                answer = response.json().get('response', '我没有接收到有效回复。')
                self.log_signal.emit(f"AI 回复: {answer}")
                speak(answer)
            else:
                self.log_signal.emit("错误：无法连接到 Ollama 服务。")
        except Exception as e:
            self.log_signal.emit(f"系统运行异常: {str(e)}")

# --- HUD 动态旋转核心组件 ---
class AICoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def paintEvent(self, event):
        self.angle = (self.angle + 2) % 360
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2
        r = min(cx, cy) - 20

        # 外层旋转弧线
        painter.setPen(QPen(QColor(0, 243, 255), 3))
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle)
        painter.drawArc(-r, -r, 2 * r, 2 * r, 0, 2000)
        painter.restore()

        # 中心发光核
        painter.setBrush(QColor(0, 243, 255, 150))
        painter.drawEllipse(cx - r // 2, cy - r // 2, r, r)

# --- 主 HUD 界面窗口 ---
class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S. SYSTEM TERMINAL v2.0")
        self.resize(1000, 600)
        self.setStyleSheet("background: #050b14; color: #00f3ff; font-family: Consolas;")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # 左侧：系统日志区
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("SYSTEM LOGS:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background: rgba(0,0,0,0.5); border: 1px solid #00f3ff; color: #00ff88;")
        left_layout.addWidget(self.log_box)
        layout.addLayout(left_layout, 1)

        # 中间：旋转核心
        layout.addWidget(AICoreWidget(), 2)

        # 右侧：控制交互区
        right_layout = QVBoxLayout()
        self.btn = QPushButton("🎙️ 激活语音输入")
        self.btn.setStyleSheet("padding: 20px; border: 2px solid #00f3ff; border-radius: 10px; font-weight: bold;")
        self.btn.clicked.connect(self.listen_thread)
        right_layout.addWidget(self.btn)
        layout.addLayout(right_layout, 1)

        self.add_log("J.A.R.V.I.S. v2.0 系统已就绪。")

    def add_log(self, text):
        self.log_box.append(f"> {text}")

    def listen_thread(self):
        threading.Thread(target=self.start_listen).start()

    def start_listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.add_log("正在聆听环境语音...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language='zh-CN')
                self.add_log(f"用户输入: {text}")
                self.brain = JarvisBrain(text)
                self.brain.log_signal.connect(self.add_log)
                self.brain.start()
            except Exception:
                self.add_log("未捕获到清晰语音，请重试。")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisHUD()
    window.show()
    sys.exit(app.exec())
