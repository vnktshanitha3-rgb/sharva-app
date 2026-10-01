import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import platform

# Android Specific Services & Vibration Setup
if platform == 'android':
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    
    def trigger_emergency_vibration():
        """Government rain/emergency siren alert laaga continuous vibration trigger chesthundi"""
        try:
            activity = PythonActivity.mActivity
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            if vibrator and vibrator.hasVibrator():
                # [delay, vibrate, pause, vibrate...] continuous emergency pattern
                pattern = [0, 600, 200, 600, 200, 1000]
                vibrator.vibrate(pattern, -1)
        except Exception as e:
            print(f"Vibration error: {e}")
else:
    def trigger_emergency_vibration():
        print("[Simulated] BZZZZ! BZZZZ! Emergency Vibration Triggered!")

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
            # Threat unte ventane Emergency Vibration trigger avthundi!
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
