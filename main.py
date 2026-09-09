from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import re

RISK_WORDS = ["debit", "debited", "blocked", "kyc", "urgent", "lottery", "gift", "electricity", "pan card", "update", "suspended"]
SUSPICIOUS_DOMAINS = ["bit.ly", "tinyurl", "ngrok", ".apk", "is.gd", "t.co"]

class SharvaApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.layout.add_widget(Label(text="🛡️ SHARVA SECURITY", font_size='22sp', bold=True, size_hint_y=0.2))
        self.input_text = TextInput(hint_text="SMS ఇక్కడ పేస్ట్ చేయండి...", size_hint_y=0.4)
        self.layout.add_widget(self.input_text)
        self.scan_btn = Button(text="స్కాన్ చేయి", size_hint_y=0.2, background_color=(0.14, 0.38, 0.92, 1))
        self.scan_btn.bind(on_press=self.scan_message)
        self.layout.add_widget(self.scan_btn)
        self.result_label = Label(text="", font_size='16sp', size_hint_y=0.2)
        self.layout.add_widget(self.result_label)
        return self.layout

    def scan_message(self, instance):
        text = self.input_text.text.lower()
        score = 0
        if re.search(r'\b\d{4,6}\b', text): score += 30
        if any(w in text for w in RISK_WORDS): score += 40
        if any(d in text for d in SUSPICIOUS_DOMAINS): score += 30
        
        if score >= 60:
            self.result_label.color = (1, 0, 0, 1)
            self.result_label.text = f"🚨 ప్రమాదం! ఫ్రాడ్ మెసేజ్ ({score}/100)"
        elif score > 0:
            self.result_label.color = (1, 0.7, 0, 1)
            self.result_label.text = "⚠️ జాగ్రత్త అవసరం!"
        else:
            self.result_label.color = (0, 1, 0, 1)
            self.result_label.text = "✅ సురక్షితం"

if __name__ == '__main__':
    SharvaApp().run()

