from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import re
import os

FONT = "NotoSansTelugu.ttf" if os.path.exists("NotoSansTelugu.ttf") else None

RISK_WORDS = [
    "debit", "debited", "blocked", "kyc", "urgent", "lottery", "gift", 
    "electricity", "pan card", "update", "suspended", "otp", "account",
    "power", "disconnect", "winner", "reward", "khata", "bill",
    "ఓటీపీ", "ఖాతా", "విద్యుత్", "నిలిపివేయబడింది", "కరెంట్", "లాటరీ", "నగదు"
]
SUSPICIOUS_DOMAINS = ["bit.ly", "tinyurl", "ngrok", ".apk", "is.gd", "t.co", "http:", "https:"]

class SharvaApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        # Title
        self.layout.add_widget(Label(
            text="SHARVA SECURITY\n(శర్వ సెక్యూరిటీ)", 
            font_size='20sp', 
            bold=True, 
            size_hint_y=0.18,
            font_name=FONT,
            halign='center'
        ))
        
        # Text Input
        self.input_text = TextInput(
            hint_text="SMS ఇక్కడ పేస్ట్ చేయండి / Paste SMS here...", 
            size_hint_y=0.42,
            multiline=True,
            font_size='16sp',
            font_name=FONT
        )
        self.layout.add_widget(self.input_text)
        
        # Scan Button
        self.scan_btn = Button(
            text="స్కాన్ చేయి / SCAN MESSAGE", 
            size_hint_y=0.15, 
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            font_size='16sp',
            font_name=FONT
        )
        self.scan_btn.bind(on_press=self.scan_message)
        self.layout.add_widget(self.scan_btn)
        
        # Result Output
        self.result_label = Label(
            text="మెసేజ్ తనిఖీకి సిద్ధంగా ఉంది\nReady to scan", 
            font_size='16sp', 
            size_hint_y=0.25,
            bold=True,
            font_name=FONT,
            halign='center'
        )
        self.layout.add_widget(self.result_label)
        return self.layout

    def scan_message(self, instance):
        text = self.input_text.text.lower().strip()
        
        if not text:
            self.result_label.color = (1, 1, 1, 1)
            self.result_label.text = "దయచేసి మెసేజ్ పేస్ట్ చేయండి!\nPlease enter SMS first!"
            return

        score = 0

        # Check for 4 to 6 digit OTP pattern or Telugu OTP mentions
        if re.search(r'\b\d{4,6}\b', text) or "otp" in text or "ఓటీపీ" in text:
            score += 35

        # Check for risk keywords (English & Telugu)
        if any(w in text for w in RISK_WORDS):
            score += 40

        # Check for external links
        if any(d in text for d in SUSPICIOUS_DOMAINS):
            score += 35
        
        # Result Evaluation
        if score >= 60:
            self.result_label.color = (1, 0.1, 0.1, 1)  # Red Alert
            self.result_label.text = f"🚨 మోసం! OTP ఎవరికీ చెప్పకండి!\nDANGER FRAUD! DO NOT SHARE OTP!\n(Risk Score: {score}/100)"
        elif score > 0:
            self.result_label.color = (1, 0.7, 0, 1)  # Orange Alert
            self.result_label.text = f"⚠️ జాగ్రత్త! అనుమానాస్పద మెసేజ్\nWARNING: Check details carefully.\n(Risk Score: {score}/100)"
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)  # Green Safe
            self.result_label.text = "✅ సురక్షితమైనది / SAFE MESSAGE"

if __name__ == '__main__':
    SharvaApp().run()
