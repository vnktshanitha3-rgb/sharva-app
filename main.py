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
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Android Specific Services, Hardware Siren, Vibration & Emergency Full-Screen Flash Alert
if platform == 'android':
    from jnius import autoclass, PythonJavaClass, java_method
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    AudioManager = autoclass('android.media.AudioManager')
    ToneGenerator = autoclass('android.media.ToneGenerator')
    AlertDialogBuilder = autoclass('android.app.AlertDialog$Builder')

    class RunnableWrapper(PythonJavaClass):
        __javainterfaces__ = ['java/lang/Runnable']
        def __init__(self, func):
            super().__init__()
            self.func = func
        @java_method('()V')
        def run(self):
            self.func()

    def trigger_emergency_vibration():
        """సైరన్ అలారం మరియు బలమైన వైబ్రేషన్"""
        try:
            tone_gen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
            tone_gen.startTone(ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK, 1500)
        except Exception as tone_e:
            print(f"Sound error: {tone_e}")

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

                effect = VibrationEffect.createOneShot(1800, VibrationEffect.DEFAULT_AMPLITUDE)
                vibrator.vibrate(effect, audio_attrs)
        except Exception as e:
            try:
                activity = PythonActivity.mActivity
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                vibrator.vibrate(1500)
            except Exception as inner_e:
                print(f"Vibration error: {inner_e}")

    def show_government_flash_alert(title, message, is_danger=True):
        """ప్రభుత్వ ఎమర్జెన్సీ బ్రాడ్‌కాస్ట్ తరహా ఫ్లాష్ అలర్ట్ బాక్స్ (స్వచ్ఛమైన తెలుగు)"""
        def _show():
            try:
                activity = PythonActivity.mActivity
                builder = AlertDialogBuilder(activity)
                builder.setTitle(title)
                builder.setMessage(message)
                builder.setCancelable(False)
                button_text = "నేను అర్థం చేసుకున్నాను (OK)" if is_danger else "సరే (OK)"
                builder.setPositiveButton(button_text, None)
                
                dialog = builder.create()
                dialog.setCanceledOnTouchOutside(False)
                dialog.show()
            except Exception as e:
                print(f"Flash Alert Error: {e}")

        activity = PythonActivity.mActivity
        activity.runOnUiThread(RunnableWrapper(_show))

else:
    def trigger_emergency_vibration():
        print("[Simulated] BZZZZ! SIREN SOUND TRIGGERED!")

    def show_government_flash_alert(title, message, is_danger=True):
        print(f"\n================ FLASH ALERT ================\n[ {title} ]\n{message}\n=============================================\n")

# తెలుగు ఫాంట్ లోడ్ చేయడం
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

# బలమైన ఆఫ్‌లైన్ ఏఐ డిటెక్షన్ డేటాబేస్ (Advanced Offline AI Engine)
OFFLINE_FRAUD_PATTERNS = [
    (r'(blocked|debit|kyc|pan card|suspended|verify|update.*account|khata|ఖాతా|నిలిపివేయబడింది)', 45),
    (r'(otp|one time password|\b\d{4,6}\b.*(secret|share|verify)|ఓటీపీ)', 40),
    (r'(electricity|power supply|disconnected|tonight|bill.*due|విద్యుత్|కరెంట్)', 45),
    (r'(part-time|work from home|per day|earn.*daily|rating task|review work|youtube.*like|telegram)', 50),
    (r'(\.apk|bit\.ly|tinyurl|is\.gd|ngrok|t\.me|wa\.me|t\.co|@hr_|http:|https:)', 45),
    (r'(e-challan|court summons|traffic fine|challan.*fine|vehicle.*registration)', 50),
    (r'(indiapost|parcel|package.*not delivered|address.*incorrect|update.*residence)', 45)
]

class SharvaApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.title_label = Label(
            text="శర్వా సైబర్ రక్షణ\n[ SHARVA CYBER DEFENSE ]",
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
        
        self.input_text = TextInput(
            hint_text="సందేశం ఇక్కడ నమోదు చేయండి (Paste SMS here)...",
            size_hint_y=0.35,
            multiline=True,
            font_size='16sp',
            line_spacing=4,
            **font_setting
        )
        layout.add_widget(self.input_text)
        
        self.scan_btn = Button(
            text="AI తనిఖీ చేయండి (AI SCAN NOW)",
            size_hint_y=0.12,
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            font_size='16sp',
            **font_setting
        )
        self.scan_btn.bind(on_press=self.start_scan)
        layout.add_widget(self.scan_btn)
        
        self.result_label = Label(
            text="రక్షణ వ్యవస్థ సిద్ధంగా ఉంది\nసందేశాన్ని స్కాన్ చేయండి",
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
                print(f"Permission error: {e}")

    def start_scan(self, instance):
        text = self.input_text.text.strip()
        if not text:
            self.result_label.color = (1, 1, 1, 1)
            self.result_label.text = "దయచేసి SMS నమోదు చేయండి!"
            return

        self.result_label.color = (1, 0.8, 0.2, 1)
        self.result_label.text = "పరిశీలిస్తోంది...\nAI Analyzing..."
        self.scan_btn.disabled = True

        threading.Thread(target=self.process_hybrid_ai, args=(text,)).start()

    def process_hybrid_ai(self, text):
        prompt = (
            f"You are a cyber security AI defense system. Analyze this SMS: '{text}'. "
            "Detect phishing, bank scams, job frauds, APK threats, or genuine messages. "
            "Reply strictly in pure natural Telugu with a 2-line direct warning. "
            "Start your reply with [FRAUD] if it is dangerous, or [SAFE] if it is completely safe."
        )

        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # 1. ఆన్‌లైన్ జెమిని ఏఐ ప్రయత్నం
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
                self.handle_ai_response(ai_text, mode="ONLINE GEMINI AI")
                return
        except Exception as e:
            print(f"Online AI indisponibil: {e}. ఆఫ్‌లైన్ స్మార్ట్ ఏఐ రక్షణకు మారుతోంది.")

        # 2. ఆఫ్‌లైన్ స్మార్ట్ ఏఐ రక్షణ (నెట్ లేకపోయినా పనిచేస్తుంది)
        self.process_offline_ai(text)

    @mainthread
    def handle_ai_response(self, ai_reply, mode="ONLINE AI"):
        self.scan_btn.disabled = False
        is_fraud = "[FRAUD]" in ai_reply.upper() or "మోసం" in ai_reply or "ప్రమాదం" in ai_reply
        clean_telugu = ai_reply.replace("[FRAUD]", "").replace("[SAFE]", "").strip()

        if is_fraud:
            trigger_emergency_vibration()
            self.result_label.color = (1, 0.1, 0.1, 1)
            self.result_label.text = f"[ ప్రమాదం - సైబర్ మోసం! ]\n({mode})"
            
            full_warning = (
                f"అత్యవసర సైబర్ భద్రతా హెచ్చరిక!\n\n"
                f"{clean_telugu}\n\n"
                f"సూచన: ఇందులో ఉన్న లింకులు నొక్కకండి, ఎవరికీ డబ్బు లేదా OTP పంపకండి!"
            )
            show_government_flash_alert("సైబర్ మోసం గుర్తించబడింది!", full_warning, is_danger=True)
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = f"[ సురక్షితం / SAFE ]\n({mode})"
            show_government_flash_alert("సురక్షిత సందేశం", f"ఈ సందేశంలో ఎటువంటి మోసం కనిపించలేదు.\n\n{clean_telugu}", is_danger=False)

    @mainthread
    def process_offline_ai(self, text):
        self.scan_btn.disabled = False
        lower_t = text.lower()
        threat_score = 0
        detected_reasons = []

        for pattern, weight in OFFLINE_FRAUD_PATTERNS:
            if re.search(pattern, lower_t):
                threat_score += weight
                if "apk" in lower_t:
                    detected_reasons.append("హానికరమైన యాప్ (APK) ఫైల్ ఉంది")
                elif "telegram" in lower_t or "part-time" in lower_t:
                    detected_reasons.append("పార్ట్‌టైమ్ జాబ్ / టెలిగ్రామ్ టాస్క్ మోసం")
                elif "electricity" in lower_t or "power" in lower_t:
                    detected_reasons.append("నకిలీ విద్యుత్ బిల్లు హెచ్చరిక")
                elif "blocked" in lower_t or "kyc" in lower_t:
                    detected_reasons.append("బ్యాంక్ ఖాతా నిలిపివేత / KYC మోసం")

        if threat_score >= 40:
            trigger_emergency_vibration()
            self.result_label.color = (1, 0.1, 0.1, 1)
            self.result_label.text = "[ ప్రమాదం - సైబర్ మోసం! ]\n(OFFLINE AI DEFENSE)"

            reasons_text = ", ".join(list(set(detected_reasons))[:2]) if detected_reasons else "అనుమానాస్పద లింకులు మరియు మోసపూరిత సమాచారం ఉంది"
            offline_warning = (
                f"అత్యవసర సైబర్ భద్రతా హెచ్చరిక! (ఆఫ్‌లైన్ రక్షణ)\n\n"
                f"కారణం: {reasons_text}.\n\n"
                f"తీవ్రత: {min(threat_score, 100)}/100\n\n"
                f"ఈ సందేశం ద్వారా మీ బ్యాంక్ ఖాతా ఖాళీ అయ్యే లేదా మీ ఫోన్ హ్యాక్ అయ్యే ప్రమాదం ఉంది. లింక్ అస్సలు నొక్కవద్దు!"
            )
            show_government_flash_alert("తీవ్రమైన సైబర్ ప్రమాదం!", offline_warning, is_danger=True)
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ సురక్షితం / SAFE ]\n(OFFLINE AI)"
            show_government_flash_alert("సురక్షిత సందేశం", "ఆఫ్‌లైన్ విశ్లేషణ ప్రకారం ఈ సందేశంలో ఎటువంటి సైబర్ ముప్పు కనపడలేదు.", is_danger=False)

if __name__ == '__main__':
    SharvaApp().run()
