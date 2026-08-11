import sys
import random
import threading
import requests
import speech_recognition as sr
import pyttsx3
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- 语音合成引擎 ---
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- 核心大脑：负责请求 Ollama 和 说话 ---
class JarvisBrain(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            self.log_signal.emit(f"AI 正在思考: {self.prompt}...")
            # 连接 Ollama
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3", 
                "prompt": self.prompt,
                "stream": False
            })
            if response.status_code == 200:
                answer = response.json().get('response', '我没听清')
                self.log_signal.emit(f"AI 回复: {answer}")
                speak(answer) # 朗读回复
            else:
                self.log_signal.emit("错误：无法连接到 Ollama")
        except Exception as e:
            self.log_signal.emit(f"系统错误: {str(e)}")

# --- 视觉动画组件 ---
class AICoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def paintEvent(self, event):
        self.angle += 2
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width()//2, self.height()//2
        r = min(cx, cy) - 20
        # 旋转圆环
        painter.setPen(QPen(QColor(0, 243, 255), 3))
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle)
        painter.drawArc(-r, -r, 2*r, 2*r, 0, 2000)
        painter.restore()
        # 中心核心
        painter.setBrush(QColor(0, 243, 255, 150))
        painter.drawEllipse(cx-r//2, cy-r//2, r, r)

# --- 主界面 ---
class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS OS v2.0")
        self.resize(1000, 600)
        self.setStyleSheet("background: #050b14; color: #00f3ff; font-family: Consolas;")
        
        main = QWidget()
        self.setCentralWidget(main)
        layout = QHBoxLayout(main)

        # 左侧：状态栏
        left = QVBoxLayout()
        left.addWidget(QLabel("SYSTEM: ONLINE"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background: rgba(0,0,0,0.5); border: 1px solid #00f3ff;")
        left.addWidget(self.log_box)
        layout.addLayout(left, 1)

        # 中间：核心动画
        layout.addWidget(AICoreWidget(), 2)

        # 右侧：语音按钮
        right = QVBoxLayout()
        self.btn = QPushButton("🎙️ 激活语音输入")
        self.btn.setStyleSheet("padding: 20px; border: 2px solid #00f3ff; border-radius: 10px;")
        self.btn.clicked.connect(self.listen_thread)
        right.addWidget(self.btn)
        layout.addLayout(right, 1)

    def add_log(self, text):
        self.log_box.append(f"> {text}")

    def listen_thread(self):
        threading.Thread(target=self.start_listen).start()

    def start_listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.add_log("正在聆听...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language='zh-CN')
                self.add_log(f"你: {text}")
                # 触发大脑
                self.brain = JarvisBrain(text)
                self.brain.log_signal.connect(self.add_log)
                self.brain.start()
            except:
                self.add_log("无法识别语音")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = JarvisHUD()
    w.show()
    sys.exit(app.exec())

