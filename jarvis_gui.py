import sys, threading, requests, json, asyncio, io, queue, os
import pyaudio, pygame, numpy as np, math, edge_tts
from vosk import Model, KaldiRecognizer
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF

# ================= 配置区 =================
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_PATH = "D:\\Jarvis\\vosk-model-small-cn-0.22\\model"
MODEL_NAME = "qwen2.5:1.5b"
VOICE_NAME = "zh-CN-XiaoxiaoNeural"
MEMORY_FILE = "jarvis_memory.json"

# 中断关键词
INTERRUPT_KEYWORDS = ["停一下", "暂停", "停", "我打断一下", "停下来", "停止"]

# 角色设定触发词
ROLE_TRIGGERS = ["扮演", "你现在是", "你的角色是", "设定你是", "从现在开始你是", "角色设定", "设定角色", "你就是"]
# ==========================================

class JarvisUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(360, 360)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # 加载记忆
        self.memory = self._load_memory()
        self.role_prompt = self.memory.get("role", 
            "你叫糖果，是一个活泼有趣的AI助手，回答简短、幽默、有温度，像朋友一样聊天。")
        self.history = self.memory.get("history", [])
        
        # 语音识别
        self.model = Model(MODEL_PATH)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.interrupt_rec = KaldiRecognizer(self.model, 16000)
        
        # 状态
        self.state = "IDLE"
        self.vol = 0.0
        self.smooth_vol = 0.0
        self.phase = 0.0
        
        self._stop_flag = False
        self._reset_interrupt_req = False
        
        pygame.mixer.init()
        self.audio_queue = queue.Queue()
        self.running = True
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(30)
        
        threading.Thread(target=self._audio_loop, daemon=True).start()
        threading.Thread(target=self._playback_loop, daemon=True).start()
        
        print(f"[系统] 已启动")
        print(f"[角色] {self.role_prompt[:40]}...")

    def _load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_memory(self):
        try:
            data = {
                "role": self.role_prompt,
                "history": self.history[-30:]
            }
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[保存失败] {e}")

    # ========== 物理键盘打断 ==========
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            print("\n[物理打断] 按下空格键")
            self._request_stop()
            event.accept()
            return
        super().keyPressEvent(event)

    def _request_stop(self):
        self._stop_flag = True
        try:
            pygame.mixer.music.stop()
        except:
            pass
            
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()
            except queue.Empty:
                break
                
        self.state = "IDLE"
        self._reset_interrupt_req = True

    # ========== UI ==========
    def update_ui(self):
        self.smooth_vol += (self.vol - self.smooth_vol) * 0.2
        self.phase += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        col = (QColor(0, 210, 255) if self.state == "IDLE" 
               else QColor(190, 90, 255) if self.state == "THINKING" 
               else QColor(255, 180, 0))
        for ring in range(3):
            poly = QPolygonF()
            freq = 3 + ring
            amp = self.smooth_vol * (15 + ring * 5) + 5
            for i in range(100):
                angle = (2 * math.pi / 100) * i
                r = 60 + math.sin(angle * freq + self.phase) * amp
                poly.append(QPointF(cx + r * math.cos(angle), cy + r * math.sin(angle)))
            painter.setPen(QPen(QColor(col.red(), col.green(), col.blue(), 180), 3))
            painter.drawPolygon(poly)

    # ========== 播放线程 ==========
    def _playback_loop(self):
        while self.running:
            try:
                audio_data, text = self.audio_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            
            if self._stop_flag:
                self._stop_flag = False
                self.audio_queue.task_done()
                continue
            
            self.state = "SPEAKING"
            print(f"\n[糖果]: {text}")
            
            try:
                pygame.mixer.music.load(io.BytesIO(audio_data))
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(200)
                    if self._stop_flag:
                        pygame.mixer.music.stop()
                        break
            except Exception as e:
                print(f"[播放错误] {e}")
            finally:
                self._stop_flag = False
                if self.state == "SPEAKING":
                    self.state = "IDLE"
                self.audio_queue.task_done()

    # ========== 音频识别线程 ==========
    def _audio_loop(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, 
                        input=True, frames_per_buffer=1024)
        
        try:
            while self.running:
                data = stream.read(1024, exception_on_overflow=False)
                rms = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                self.vol = float(np.sqrt(np.mean(rms**2)) / 50.0)
                
                if self._reset_interrupt_req:
                    try:
                        self.interrupt_rec.Reset()
                        self.rec.Reset()
                    except:
                        pass
                    self._reset_interrupt_req = False
                
                # ===== 播报状态：流式监测关键词 =====
                if self.state == "SPEAKING":
                    self.interrupt_rec.AcceptWaveform(data)
                    partial = json.loads(self.interrupt_rec.PartialResult()).get("partial", "").replace(" ", "")
                    
                    if any(kw in partial for kw in INTERRUPT_KEYWORDS):
                        print(f"\n[语音打断] 匹配关键词：{partial}")
                        self._request_stop()
                    continue
                
                # ===== 空闲状态：正常监听 =====
                if self.state == "IDLE" and self.rec.AcceptWaveform(data):
                    res = json.loads(self.rec.Result())
                    text = res.get("text", "").replace(" ", "").strip()
                    if len(text) > 1:
                        print(f"\n[听到]: {text}")
                        self.state = "THINKING"
                        threading.Thread(target=self._handle_input, args=(text,), daemon=True).start()
        except Exception as e:
            pass
        finally:
            try:
                stream.stop_stream()
                stream.close()
                p.terminate()
            except:
                pass

    # ========== AI 逻辑响应 ==========
    def _handle_input(self, text):
        try:
            if self._is_role_cmd(text):
                self._update_role(text)
                self._speak("好的，设定已更新，我现在开始进入角色。")
                return
            
            messages = [{"role": "system", "content": self.role_prompt}]
            messages.extend(self.history[-20:])
            messages.append({"role": "user", "content": text})
            
            payload = {
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9
                }
            }
            res = requests.post(OLLAMA_URL, json=payload, timeout=60)
            reply = res.json().get("message", {}).get("content", "").strip()
            
            if not reply:
                self.state = "IDLE"
                return
            
            self.history.append({"role": "user", "content": text})
            self.history.append({"role": "assistant", "content": reply})
            if len(self.history) > 40:
                self.history = self.history[-40:]
            self._save_memory()
            
            self._speak(reply)
        except Exception as e:
            print(f"[AI回复错误] {e}")
            self.state = "IDLE"

    def _is_role_cmd(self, text):
        return any(kw in text for kw in ROLE_TRIGGERS)

    def _update_role(self, text):
        self.role_prompt = (
            f"角色设定：{text}。"
            f"你必须严格按照这个角色的性格、语气说话，不要跳出角色，不要提及你是AI。"
            f"回答简短自然。"
        )
        self._save_memory()

    def _speak(self, text):
        try:
            audio = asyncio.run(self._tts(text))
            self.audio_queue.put((audio, text))
        except Exception as e:
            print(f"[TTS错误] {e}")
            self.state = "IDLE"

    async def _tts(self, text):
        comm = edge_tts.Communicate(text, VOICE_NAME)
        buf = io.BytesIO()
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        return buf.getvalue()

    def closeEvent(self, event):
        self.running = False
        self._stop_flag = True
        self._save_memory()
        try:
            pygame.mixer.quit()
        except:
            pass
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = JarvisUI()
    gui.show()
    sys.exit(app.exec())