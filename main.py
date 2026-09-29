import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

# Check if local font file genuinely exists, else fallback to default system font
FONT_TARGET = None
for f in ["NotoSansTelugu-Regular.ttf", "telugu_font.ttf", "suranna.ttf"]:
    if os.path.exists(f):
        FONT_TARGET = f
        break

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
        
        # Title Label
        title_kwargs = {'font_name': FONT_TARGET} if FONT_TARGET else {}
        self.title_label = Label(
            text="SHARVA SECURITY\nరక్షణ కవచం",
            font_size='22sp',
            bold=True,
            size_hint_y=0.15,
            halign='center',
            **title_kwargs
        )
        layout.add_widget(self.title_label)
        
        # SMS Input
        input_kwargs = {'font_name': FONT_TARGET} if FONT_TARGET else {}
        self.input_text = TextInput(
            hint_text="SMS ఇక్కడ పేస్ట్ చేయండి / Paste SMS here...",
            size_hint_y=0.35,
            multiline=True,
            font_size='16sp',
            **input_kwargs
        )
        layout.add_widget(self.input_text)
        
        # Scan Button
        btn_kwargs = {'font_name': FONT_TARGET} if FONT_TARGET else {}
        self.scan_btn = Button(
            text="తనిఖీ చేయండి / SCAN MESSAGE",
            size_hint_y=0.12,
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            font_size='16sp',
            **btn_kwargs
        )
        self.scan_btn.bind(on_press=self.scan_message)
        layout.add_widget(self.scan_btn)
        
        # Result Label
        result_kwargs = {'font_name': FONT_TARGET} if FONT_TARGET else {}
        self.result_label = Label(
            text="సందేశం తనిఖీకి సిద్ధంగా ఉంది\nReady to scan",
            font_size='16sp',
            size_hint_y=0.38,
            bold=True,
            halign='center',
            **result_kwargs
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
            self.result_label.text = f"[ ప్రమాదం - సైబర్ మోసం! ]\n{detail}\n(ప్రమాద తీవ్రత: {score}/100)"
        elif score > 0:
            self.result_label.color = (1, 0.7, 0, 1)
            self.result_label.text = f"[ హెచ్చరిక ]\nఅనుమానాస్పద సందేశం, జాగ్రత్త!\nWARNING: Suspicious message.\n(ప్రమాద తీవ్రత: {score}/100)"
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ సురక్షితం ]\nఈ సందేశం క్షేమకరం / SAFE MESSAGE"

if __name__ == '__main__':
    SharvaApp().run()
