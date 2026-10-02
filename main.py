import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import platform

# Android Specific Services & Vibration + Sound Alert Setup (Android 14 / HyperOS Support)
if platform == 'android':
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    AudioManager = autoclass('android.media.AudioManager')
    ToneGenerator = autoclass('android.media.ToneGenerator')
    
    def trigger_emergency_vibration():
        """Redmi 14C / Android 14 HyperOS lo force vibration mariyu Siren Sound trigger chese code"""
        # 1. Loud Emergency Siren / Alarm Beep Sound
        try:
            tone_gen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
            # Emergency Ringback / Siren Beep tone for 1.2 seconds
            tone_gen.startTone(ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK, 1200)
        except Exception as tone_e:
            print(f"Sound error: {tone_e}")

        # 2. Hardware Force Vibration
        try:
            activity = PythonActivity.mActivity
            sdk_int = Build_VERSION.SDK_INT

            # Android 12+ (API 31, 33, 34) kosam VibratorManager
            if sdk_int >= 31:
                vibrator_manager = activity.getSystemService(Context.VIBRATOR_MANAGER_SERVICE)
                vibrator = vibrator_manager.getDefaultVibrator()
            else:
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

            if vibrator and vibrator.hasVibrator():
                VibrationEffect = autoclass('android.os.VibrationEffect')
                AudioAttributesBuilder = autoclass('android.media.AudioAttributes$Builder')
                AudioAttributes = autoclass('android.media.AudioAttributes')

                # USAGE_ALARM ద్వారా HyperOS లో సైలెంట్ కాకుండా ఫోర్స్ వైబ్రేషన్ వస్తుంది
                audio_attrs = AudioAttributesBuilder() \
                    .setUsage(AudioAttributes.USAGE_ALARM) \
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION) \
                    .build()

                # 1.5 సెకన్లు బలంగా వైబ్రేట్ అవుతుంది
                effect = VibrationEffect.createOneShot(1500, VibrationEffect.DEFAULT_AMPLITUDE)
                vibrator.vibrate(effect, audio_attrs)
        except Exception as e:
            try:
                # Fallback standard vibration
                activity = PythonActivity.mActivity
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                vibrator.vibrate(1000)
            except Exception as inner_e:
                print(f"Vibration error: {inner_e}")
else:
    def trigger_emergency_vibration():
        print("[Simulated] BZZZZ! BEEP! BEEP! Emergency Vibration and Sound Triggered!")

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
        # Spacing mariyu Padding
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
            text="SCAN NOW / తనిఖీ చేయండి",
            size_hint_y=0.12,
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            font_size='16sp',
            **font_setting
        )
        self.scan_btn.bind(on_press=self.scan_message)
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
        # App open avvagane Android permissions auto ga aduguthundi
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

    def scan_message(self, instance):
        text = self.input_text.text.lower().strip()
        
        if not text:
            self.result_label.color = (1, 1, 1, 1)
            self.result_label.text = "Please enter SMS text!\nదయచేసి SMS రాయండి!"
            return

        score = 0
        has_otp = bool(re.search(r'\b\d{4,6}\b', text) or "otp" in text or "ఓటీపీ" in text)
        has_risk_words = any(w in text for w in RISK_KEYWORDS)
        has_links = any(d in text for d in SUSPICIOUS_LINKS)

        if has_otp:
            score += 35
        if has_risk_words:
            score += 40
        if has_links:
            score += 35

        if score >= 60:
            # Threat unte ventane Emergency Vibration tho paatu Siren Sound kooda vasthundi!
            trigger_emergency_vibration()
            self.result_label.color = (1, 0.1, 0.1, 1)
            detail = "SUSPICIOUS LINK DETECTED!\nలింక్ ఓపెన్ చేయకండి!" if has_links else "DO NOT SHARE OTP!\nOTP ఎవరికీ చెప్పకండి!"
            self.result_label.text = f"[ FRAUD DETECTED / ప్రమాదం! ]\n\n{detail}\n\n(తీవ్రత: {score}/100)"
        elif score > 0:
            self.result_label.color = (1, 0.7, 0, 1)
            self.result_label.text = f"[ WARNING / హెచ్చరిక! ]\n\nSuspicious Message Found\nఅనుమానాస్పద సందేశం\n\n(తీవ్రత: {score}/100)"
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ SAFE / సురక్షితం ]\n\nNo threats found\nఈ సందేశం క్షేమకరం"

if __name__ == '__main__':
    SharvaApp().run()
