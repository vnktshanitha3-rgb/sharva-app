import os
import re
import json
import threading
from urllib import request

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivy.clock import mainthread

# --- Gemini API Configuration ---
GEMINI_API_KEY = "AQ.Ab8RN6KvD2RjO3BSQyFZZtp473Q1fQSQdBZ3BX2P7UIzSDEfhA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

# Android Specific Services & Vibration + Sound Alert Setup (Android 14 / HyperOS Support)
if platform == 'android':
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    AudioManager = autoclass('android.media.AudioManager')
    ToneGenerator = autoclass('android.media.ToneGenerator')
    AlertDialog = autoclass('android.app.AlertDialog$Builder')
    
    def trigger_emergency_vibration():
        """Redmi 14C / Android 14 HyperOS lo force vibration mariyu Siren Sound"""
        # 1. Loud Emergency Siren / Alarm Beep Sound
        try:
            tone_gen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
            tone_gen.startTone(ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK, 1200)
        except Exception as tone_e:
            print(f"Sound error: {tone_e}")

        # 2. Hardware Force Vibration
        try:
            activity = PythonActivity.mActivity
            sdk_int = Build_VERSION.SDK_INT

            if sdk_int >= 31:
                vibrator_manager = activity.getSystemService(Context.VIBRATOR_MANAGER_SERVICE)
                vibrator = vibrator_manager.getDefaultVibrator()
            else:
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

            if vibrator and vibrator.hasVibrator():
                VibrationEffect = autoclass('android.os.VibrationEffect')
                AudioAttributesBuilder = autoclass('android.media.AudioAttributes$Builder')
                AudioAttributes = autoclass('android.media.AudioAttributes')

                audio_attrs = AudioAttributesBuilder() \
                    .setUsage(AudioAttributes.USAGE_ALARM) \
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION) \
                    .build()

                effect = VibrationEffect.createOneShot(1500, VibrationEffect.DEFAULT_AMPLITUDE)
                vibrator.vibrate(effect, audio_attrs)
        except Exception as e:
            try:
                activity = PythonActivity.mActivity
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                vibrator.vibrate(1000)
            except Exception as inner_e:
                print(f"Vibration error: {inner_e}")

    def show_pure_telugu_dialog(title, message):
        """Android System Engine ద్వార అక్షరాలు విరిగిపోకుండా స్వచ్ఛమైన తెలుగు చూపే పాప్-అప్"""
        try:
            activity = PythonActivity.mActivity
            builder = AlertDialog(activity)
            builder.setTitle(title)
            builder.setMessage(message)
            builder.setPositiveButton("సరే (OK)", None)
            dialog = builder.create()
            dialog.show()
        except Exception as err:
            print(f"Dialog error: {err}")

else:
    def trigger_emergency_vibration():
        print("[Simulated] BZZZZ! BEEP! BEEP! Emergency Triggered!")

    def show_pure_telugu_dialog(title, message):
        print(f"\n--- [ {title} ] ---\n{message}\n------------------\n")

# Locate bundled font
FONT_NAME = "NotoSansTelugu-Regular.ttf"
if os.path.exists(FONT_NAME):
    font_path = FONT_NAME
else:
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FONT_NAME)

try:
    if os.path.exists(font_path):
        LabelBase.register(name="TeluguFont", fn_regular=font_path)
        USE_FONT = "TeluguFont"
    else:
        USE_FONT = None
except Exception:
    USE_FONT = None

font_setting = {'font_name': USE_FONT} if USE_FONT else {}

# Phishing detection keywords
RISK_KEYWORDS = [
    "debit", "debited", "blocked", "kyc", "urgent", "lottery", "gift", 
    "electricity", "pan card", "update", "suspended", "otp", "account",
    "power", "disconnect", "winner", "reward", "khata", "bill",
    "ఓటీపీ", "ఖాతా", "విద్యుత్", "నిలిపివేయబడింది", "కరెంట్", "లాటరీ", "బ్యాంకు"
]

SUSPICIOUS_LINKS = ["bit.ly", "tinyurl", "ngrok", ".apk", "is.gd", "t.co", "http:", "https:"]

class SharvaApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title Label
        self.title_label = Label(
            text="SHARVA SECURITY\n[ Cyber Defense / రక్షణ ]",
            font_size='22sp',
            bold=True,
            line_height=1.4,
            size_hint_y=0.15,
            halign='center',
            valign='middle',
            **font_setting
        )
        self.title_label.bind(size=lambda s, w: setattr(s, 'text_size', w))
        layout.add_widget(self.title_label)
        
        # Input Box
        self.input_text = TextInput(
            hint_text="Paste SMS here / SMS ఇక్కడ పేస్ట్ చేయండి...",
            size_hint_y=0.35,
            multiline=True,
            font_size='16sp',
            line_spacing=4,
            **font_setting
        )
        layout.add_widget(self.input_text)
        
        # Scan Button
        self.scan_btn = Button(
            text="AI SCAN NOW / తనిఖీ చేయండి",
            size_hint_y=0.12,
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            font_size='16sp',
            **font_setting
        )
        self.scan_btn.bind(on_press=self.start_scan)
        layout.add_widget(self.scan_btn)
        
        # Result Label
        self.result_label = Label(
            text="Ready to Scan\nసందేశం తనిఖీకి సిద్ధంగా ఉంది",
            font_size='16sp',
            line_height=1.4,
            size_hint_y=0.38,
            bold=True,
            halign='center',
            valign='middle',
            **font_setting
        )
        self.result_label.bind(size=lambda s, w: setattr(s, 'text_size', w))
        layout.add_widget(self.result_label)
        
        return layout

    def on_start(self):
        if platform == 'android':
            try:
                request_permissions([
                    Permission.RECEIVE_SMS,
                    Permission.READ_SMS,
                    Permission.VIBRATE,
                    Permission.POST_NOTIFICATIONS
                ])
            except Exception as e:
                print(f"Permission request error: {e}")

    def start_scan(self, instance):
        text = self.input_text.text.strip()
        if not text:
            self.result_label.color = (1, 1, 1, 1)
            self.result_label.text = "Please enter SMS text!\nదయచేసి SMS రాయండి!"
            return

        self.result_label.color = (1, 0.8, 0.2, 1)
        self.result_label.text = "Gemini AI Analyzing...\nజెమిని ఏఐ తనిఖీ చేస్తోంది..."
        self.scan_btn.disabled = True

        # AI రిక్వెస్ట్ కోసం బ్యాక్‌గ్రౌండ్ థ్రెడ్ (యాప్ హ్యాంగ్ అవ్వకుండా)
        threading.Thread(target=self.process_detection, args=(text,)).start()

    def process_detection(self, text):
        prompt = (
            f"You are a cybersecurity expert. Analyze this SMS: '{text}'. "
            "Determine if this is fraud or safe. "
            "Reply strictly in pure natural Telugu with a clear warning or advice in 2 sentences. "
            "Start your reply with [FRAUD] if danger/phishing, or [SAFE] if it is normal."
        )

        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            req = request.Request(
                GEMINI_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with request.urlopen(req, timeout=8) as response:
                res = json.loads(response.read().decode('utf-8'))
                ai_text = res['candidates'][0]['content']['parts'][0]['text']
                self.handle_result(text, ai_text)
                return
        except Exception as e:
            print(f"Gemini API fallback: {e}")

        # ఇంటర్నెట్ లేకపోయినా లోకల్ అల్గారిథమ్ ఫాల్‌బ్యాక్
        self.fallback_detection(text)

    @mainthread
    def handle_result(self, original_text, ai_reply):
        self.scan_btn.disabled = False
        is_fraud = "[FRAUD]" in ai_reply.upper() or "మోసం" in ai_reply or "ప్రమాదం" in ai_reply

        clean_telugu = ai_reply.replace("[FRAUD]", "").replace("[SAFE]", "").strip()

        if is_fraud:
            trigger_emergency_vibration()
            self.result_label.color = (1, 0.1, 0.1, 1)
            self.result_label.text = "[ FRAUD DETECTED / ప్రమాదం! ]\n\nహెచ్చరిక కింద పాప్-అప్‌లో చూడండి!"
            show_pure_telugu_dialog("హెచ్చరిక! సైబర్ మోసం", clean_telugu)
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ SAFE / సురక్షితం ]\n\nఈ సందేశం క్షేమకరం"
            show_pure_telugu_dialog("సురక్షిత సందేశం", clean_telugu)

    @mainthread
    def fallback_detection(self, text):
        self.scan_btn.disabled = False
        lower_t = text.lower()
        score = 0
        has_otp = bool(re.search(r'\b\d{4,6}\b', lower_t) or "otp" in lower_t or "ఓటీపీ" in lower_t)
        has_risk_words = any(w in lower_t for w in RISK_KEYWORDS)
        has_links = any(d in lower_t for d in SUSPICIOUS_LINKS)

        if has_otp: score += 35
        if has_risk_words: score += 40
        if has_links: score += 35

        if score >= 60:
            trigger_emergency_vibration()
            self.result_label.color = (1, 0.1, 0.1, 1)
            self.result_label.text = f"[ FRAUD DETECTED / ప్రమాదం! ]\n(తీవ్రత: {score}/100)"
            show_pure_telugu_dialog(
                "హెచ్చరిక! సైబర్ మోసం", 
                "ఇది నకిలీ మోసపూరిత సందేశం. ఇందులో ఉన్న లింక్‌లను క్లిక్ చేయకండి మరియు మీ OTP వివరాలను ఎవరికీ చెప్పవద్దు."
            )
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ SAFE / సురక్షితం ]\n\nఈ సందేశం క్షేమకరం"
            show_pure_telugu_dialog("సురక్షితం", "ఈ సందేశంలో ఎటువంటి అనుమానాస్పద లింకులు లేదా మోసాలు కనిపించలేదు.")

if __name__ == '__main__':
    SharvaApp().run()
