import sys
import random
import threading
import requests
import speech_recognition as sr
import pyttsx3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QTextEdit, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, QTime, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush

engine = pyttsx3.init()

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS 异常: {e}")

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
            }, timeout=30)
            
            if response.status_code == 200:
                answer = response.json().get('response', '未接收到有效回复')
                self.log_signal.emit(f"AI 回复: {answer}")
                speak(answer)
            else:
                self.log_signal.emit("错误：无法连接到 Ollama 服务")
        except Exception as e:
            self.log_signal.emit(f"异常: {str(e)}")

class AICoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def update_animation(self):
        self.angle = (self.angle + 2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width, height = self.width(), self.height()
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 3

        pen1 = QPen(QColor(0, 243, 255, 180), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen1)
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        painter.restore()

        pen2 = QPen(QColor(0, 243, 255, 255), 3)
        painter.setPen(pen2)
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.angle * 1.5)
        r2 = int(radius * 0.75)
        painter.drawArc(-r2, -r2, r2 * 2, r2 * 2, 0, 120 * 16)
        painter.drawArc(-r2, -r2, r2 * 2, r2 * 2, 180 * 16, 120 * 16)
        painter.restore()

        r3 = int(radius * 0.35)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 243, 255, 180)))
        painter.drawEllipse(cx - r3, cy - r3, r3 * 2, r3 * 2)

class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("J.A.R.V.I.S. SYSTEM TERMINAL v2.0")
        self.resize(1000, 650)
        self.setStyleSheet("""
            QMainWindow { background-color: #050b14; }
            QFrame#hud-box {
                background-color: rgba(6, 20, 38, 0.75);
                border: 1px solid rgba(0, 243, 255, 0.35);
                border-radius: 4px;
            }
            QLabel { color: #00f3ff; font-family: 'Consolas', monospace; }
            QTextEdit {
                background-color: transparent; border: none;
                color: #00ff88; font-family: 'Consolas', monospace; font-size: 12px;
            }
            QPushButton#voice-btn {
                background-color: transparent; border: 1px solid #00f3ff; color: #00f3ff;
                font-family: 'Consolas', monospace; font-size: 13px;
                border-radius: 18px; padding: 12px 30px; font-weight: bold;
            }
            QPushButton#voice-btn:hover { background-color: #00f3ff; color: #050b14; }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        header = QLabel("J.A.R.V.I.S. // PROTOCOL ONLINE  |  CORE: STABLE  |  LOCALHOST")
        header.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        body_layout = QHBoxLayout()

        left_box = QFrame()
        left_box.setObjectName("hud-box")
        left_layout = QVBoxLayout(left_box)
        left_layout.addWidget(QLabel("[ SYSTEM TERMINAL LOGS ]"))

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        left_layout.addWidget(self.log_box)
        body_layout.addWidget(left_box, 1)

        self.ai_core = AICoreWidget()
        body_layout.addWidget(self.ai_core, 2)

        main_layout.addLayout(body_layout)

        footer_layout = QHBoxLayout()
        self.voice_btn = QPushButton("🎙️ INITIALIZE VOICE INPUT")
        self.voice_btn.setObjectName("voice-btn")
        self.voice_btn.clicked.connect(self.listen_thread)
        footer_layout.addStretch()
        footer_layout.addWidget(self.voice_btn)
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)

        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.add_simulated_log)
        self.log_timer.start(4000)

        self.add_log("J.A.R.V.I.S. v2.0 系统已准备就绪。")

    def add_log(self, text):
        time_str = QTime.currentTime().toString("hh:mm:ss")
        self.log_box.append(f"[{time_str}] > {text}")

    def add_simulated_log(self):
        logs = ["Telemetry sync OK.", "Ollama endpoint online.", "Audio stream OK."]
        self.add_log(random.choice(logs))

    def listen_thread(self):
        threading.Thread(target=self.start_listen, daemon=True).start()

    def start_listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.add_log(">>> 正在聆听...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language='zh-CN')
                self.add_log(f"用户: {text}")
                self.brain = JarvisBrain(text)
                self.brain.log_signal.connect(self.add_log)
                self.brain.start()
            except Exception:
                self.add_log("未捕获到有效语音")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisHUD()
    window.show()
    sys.exit(app.exec())
