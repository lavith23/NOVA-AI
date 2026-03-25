import flet as ft
import speech_recognition as sr
import pyttsx3
import threading
import os
import datetime
from plyer import battery, flash, brightness
from groq import Groq

# --- CORE ENGINE SETTINGS ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Memory: Nova ko sab yaad rahega
chat_history = [{"role": "system", "content": "You are Nova, the ultimate AI OS for Boss Lavith. You have full control over his phone. Talk like a smart, futuristic companion."}]

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 185)
    # Female voice preferred for Nova
    voices = engine.getProperty('voices')
    if len(voices) > 1: engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

def main(page: ft.Page):
    page.title = "Nova AI"
    page.bgcolor = ft.colors.TRANSPARENT
    page.window_bgcolor = ft.colors.TRANSPARENT
    page.vertical_alignment = ft.MainAxisAlignment.END
    
    # UI Elements
    user_input = ft.TextField(
        hint_text="Ask Nova...",
        border=ft.InputBorder.NONE,
        expand=True,
        color=ft.colors.WHITE,
        text_size=16,
    )
    
    response_area = ft.Text("", color=ft.colors.WHITE70, size=15, weight="medium")

    # --- FEATURE: SYSTEM MASTER LOGIC ---
    def handle_system(query):
        query = query.lower()
        if "open" in query:
            app = query.replace("open", "").strip()
            speak(f"Opening {app}")
            os.system(f"monkey -p {app} -c android.intent.category.LAUNCHER 1")
            return True
        elif "flashlight" in query or "torch" in query:
            if "on" in query: flash.on(); speak("Flashlight is on, Boss.")
            else: flash.off(); speak("Flashlight is off.")
            return True
        elif "battery" in query:
            perc = battery.status['percentage']
            speak(f"Boss, your battery is at {perc} percent.")
            return True
        return False

    def process_query(query):
        response_area.value = "Processing..."
        page.update()
        
        # 1. Check System Commands First
        if not handle_system(query):
            # 2. Use AI Brain with Memory
            chat_history.append({"role": "user", "content": query})
            res = client.chat.completions.create(
                messages=chat_history,
                model="llama-3.3-70b-specdec"
            )
            reply = res.choices[0].message.content
            chat_history.append({"role": "assistant", "content": reply})
            
            response_area.value = reply
            page.update()
            threading.Thread(target=speak, args=(reply,), daemon=True).start()

    def start_listen(e):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            response_area.value = "Listening..."
            page.update()
            try:
                audio = r.listen(source, timeout=5)
                query = r.recognize_google(audio)
                user_input.value = query
                page.update()
                process_query(query)
            except:
                response_area.value = "Sorry Boss, I missed that."
                page.update()

    # --- GEMINI UI PANEL ---
    gemini_bar = ft.Container(
        content=ft.Row([
            ft.IconButton(ft.icons.ADD, icon_color=ft.colors.WHITE70),
            ft.IconButton(ft.icons.GOOGLE_LENS, icon_color=ft.colors.WHITE70),
            user_input,
            ft.Container(
                content=ft.IconButton(ft.icons.MIC_ROUNDED, icon_color=ft.colors.WHITE, on_click=start_listen),
                bgcolor=ft.colors.BLUE_700,
                shape=ft.BoxShape.CIRCLE,
                padding=2
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor="#1A1C1E",
        border_radius=40,
        padding=ft.padding.symmetric(horizontal=15, vertical=8),
        margin=ft.margin.only(bottom=20, left=10, right=10),
    )

    # Initial Greeting
    hour = datetime.datetime.now().hour
    greet = "Good Morning Boss" if hour < 12 else "Good Evening Boss"
    response_area.value = f"{greet}. Nova is ready."

    page.add(
        ft.Column([
            ft.Row([response_area], alignment=ft.MainAxisAlignment.CENTER),
            gemini_bar,
        ], alignment=ft.MainAxisAlignment.END, expand=True)
    )
    
    # Auto-speak greeting on start
    threading.Thread(target=speak, args=(greet,), daemon=True).start()

if __name__ == "__main__":
    ft.app(target=main)