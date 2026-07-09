import speech_recognition as sr
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import keyboard
import pyperclip
import pyautogui
import tkinter as tk
import time
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- 設定 ---
FS = 44100
TARGET_KEY = 'right ctrl'

class VoiceApp:
    def __init__(self):
        # Tk()をそのまま利用し、withdrawせずタスクバーにアイコン表示
        self.root = tk.Tk()
        self.root.title("DragonWords")
        
        # --- ここから書き換え（あるいは追加） ---
        try:
            # 1番で作った魔法の関数「resource_path」を使ってパスを取得
            icon_path = resource_path("DragonWhisper.ico")
            # そのパスを使ってアイコンを設定
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"アイコン読み込みエラー: {e}")
        # ----------------------------

        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)

        w, h = 250, 60
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"{w}x{h}+{sw - w - 20}+40")

        self.label = tk.Label(
            self.root, text="🎤 右Ctrlで開始", 
            font=("Meiryo", 11, "bold"), bg="#2f7", fg="white"
        )
        self.label.pack(expand=True, fill="both")

        # 閉じるボタンでcleanに終了
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.running = True

    def on_close(self):
        self.running = False
        self.root.quit()  # イベントループ停止
        self.root.destroy()

    def update_ui(self, text, bg):
        """UIの文字と色を更新する（メインスレッドから呼ぶ）"""
        self.label.config(text=text, bg=bg)
        self.root.update()

    def recognize_and_paste(self, audio_data):
        self.update_ui("⏳ 解析中...", "#ffb") 
        recognizer = sr.Recognizer()
        byte_io = io.BytesIO()
        wav.write(byte_io, FS, audio_data)
        byte_io.seek(0)
        
        with sr.AudioFile(byte_io) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language='ja-JP')
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                self.update_ui(f"✅ 入力完了", "#2af")
            except Exception:
                self.update_ui("❌ 認識失敗", "#f66")
        
        # タイマーの代わりに、Tkinterが提供する安全な待ち時間（after）を使う
        self.root.after(1500, lambda: self.update_ui("🎤 右Ctrlで開始", "#2f7"))

    def run(self):
        print("アプリ起動中...")
        try:
            while self.running:
                self.root.update()
                if keyboard.is_pressed(TARGET_KEY):
                    self.update_ui("🔴 録音中...", "#f66")
                    recording = []
                    
                    with sd.InputStream(samplerate=FS, channels=1, dtype='int16') as stream:
                        while keyboard.is_pressed(TARGET_KEY) and self.running:
                            # ここでも画面更新を行う
                            self.root.update()
                            data, _ = stream.read(1024)
                            recording.append(data)
                    
                    if recording and self.running:
                        audio_full = np.concatenate(recording, axis=0)
                        self.recognize_and_paste(audio_full)
                
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("アプリを終了しました")
        except Exception as e:
            print(f"停止しました: {e}")

if __name__ == "__main__":
    try:
        app = VoiceApp()
        app.run()
    except KeyboardInterrupt:
        print("アプリを終了しました")
