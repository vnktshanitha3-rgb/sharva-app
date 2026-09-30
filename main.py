import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase

# Search and forcefully register Telugu font
TELUGU_FONT = None
candidates = [
    "NotoSansTelugu-Regular.ttf",
    "telugu_font.ttf",
    os.path.join(os.path.dirname(__file__), "NotoSansTelugu-Regular.ttf"),
    os.path.join(os.path.dirname(__file__), "telugu_font.ttf"),
]

for font_path in candidates:
    if os.path.exists(font_path):
        TELUGU_FONT = font_path
        break

if not TELUGU_FONT:
    # If path search fails, use the direct bundled filename directly
    TELUGU_FONT = "NotoSansTelugu-Regular.ttf"

# Register as default custom font
LabelBase.register(name="TeluguFont", fn_regular=TELUGU_FONT)

RISK_KEYWORDS = [
    "debit", "debited", "blocked", "kyc", "urgent", "lottery", "gift", 
    "electricity", "pan card", "update", "suspended", "otp", "account",
    "power", "disconnect", "winner", "reward", "khata", "bill",
    "ఓటీపీ", "ఖాతా", "విద్యుత్", "నిలిపివేయబడింది", "కరెంట్", "లాటరీ"
]

SUSPICIOUS_LINKS = ["bit.ly", "tinyurl", "ngrok", ".apk", "is.gd", "t.co", "http:", "https:"]

class SharvaApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # Header Title
        self.title_label = Label(
            text="SHARVA SECURITY\nరక్షణ కవచం",
            font_name="TeluguFont",
            font_size='22sp',
            bold=True,
            size_hint_y=0.15,
            halign='center'
        )
        layout.add_widget(self.title_label)
        
        # SMS Input Field
        self.input_text = TextInput(
            hint_text="SMS ఇక్కడ పేస్ట్ చేయండి / Paste SMS here...",
            font_name="TeluguFont",
            size_hint_y=0.35,
            multiline=True,
            font_size='16sp'
        )
        layout.add_widget(self.input_text)
        
        # Scan Button
        self.scan_btn = Button(
            text="తనిఖీ చేయండి / SCAN MESSAGE",
            font_name="TeluguFont",
            size_hint_y=0.12,
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            font_size='16sp'
        )
        self.scan_btn.bind(on_press=self.scan_message)
        layout.add_widget(self.scan_btn)
        
        # Result Container
        self.result_label = Label(
            text="సందేశం తనిఖీకి సిద్ధంగా ఉంది\nReady to scan",
            font_name="TeluguFont",
            font_size='16sp',
            size_hint_y=0.38,
            bold=True,
            halign='center'
        )
        layout.add_widget(self.result_label)
        
        return layout

    def scan_message(self, instance):
        text = self.input_text.text.lower().strip()
        
        if not text:
            self.result_label.color = (1, 1, 1, 1)
            self.result_label.text = "దయచేసి SMS రాయండి!\nPlease enter SMS first!"
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
            self.result_label.color = (1, 0.1, 0.1, 1)
            if has_links:
                detail = "మోసపూరిత లింక్ ఉంది! క్లిక్ చేయకండి!\nSUSPICIOUS LINK DETECTED! DO NOT CLICK!"
            else:
                detail = "OTP ఎవరికీ చెప్పకండి!\nDO NOT SHARE OTP!"
            self.result_label.text = f"[ ప్రమాదం - సైబర్ మోసం! ]\n{detail}\n(తీవ్రత: {score}/100)"
        elif score > 0:
            self.result_label.color = (1, 0.7, 0, 1)
            self.result_label.text = f"[ హెచ్చరిక ]\nఅనుమానాస్పద సందేశం!\nWARNING: Suspicious!\n(తీవ్రత: {score}/100)"
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ సురక్షితం ]\nఈ సందేశం క్షేమకరం / SAFE"

if __name__ == '__main__':
    SharvaApp().run()
