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
        
        # Title (శర్వ రక్షణ కవచం)
        self.layout.add_widget(Label(
            text="SHARVA SECURITY\nరక్షణ కవచం", 
            font_size='22sp', 
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
            text="తనిఖీ చేయండి / SCAN MESSAGE", 
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
            text="సందేశం తనిఖీకి సిద్ధంగా ఉంది\nReady to scan", 
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
            self.result_label.text = "దయచేసి మెసేజ్ రాయండి!\nPlease enter SMS first!"
            return

        score = 0

        # Check for OTP pattern
        if re.search(r'\b\d{4,6}\b', text) or "otp" in text or "ఓటీపీ" in text:
            score += 35

        # Check for risk keywords
        if any(w in text for w in RISK_WORDS):
            score += 40

        # Check for links
        if any(d in text for d in SUSPICIOUS_DOMAINS):
            score += 35
        
        # Result Evaluation (No broken emojis)
        if score >= 60:
            self.result_label.color = (1, 0.1, 0.1, 1)
            self.result_label.text = f"[ ప్రమాదం - మోసం! ]\nOTP ఎవరికీ చెప్పకండి!\nDANGER FRAUD! DO NOT SHARE OTP!\n(Risk Score: {score}/100)"
        elif score > 0:
            self.result_label.color = (1, 0.7, 0, 1)
            self.result_label.text = f"[ హెచ్చరిక ]\nఅనుమానాస్పద సందేశం, జాగ్రత్త!\nWARNING: Suspicious message.\n(Risk Score: {score}/100)"
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ సురక్షితం ]\nఈ సందేశం క్షేమకరం / SAFE MESSAGE"

if __name__ == '__main__':
    SharvaApp().run()
