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
from kivy.utils import platform
from kivy.clock import mainthread

# --- Gemini API Configuration ---
GEMINI_API_KEY = "AQ.Ab8RN6KvD2RjO3BSQyFZZtp473Q1fQSQdBZ3BX2P7UIzSDEfhA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Critical patterns for offline evaluation
CRITICAL_FRAUD_PATTERNS = [
    r'(\.apk|download.*invoice|install.*app)',
    r'(telegram|t\.me|wa\.me|@hr_)',
    r'(part-time.*job|earn.*per day|youtube.*review|rating task)',
    r'(electricity.*disconnected|power.*cut tonight|bill.*overdue.*call)',
    r'(account.*blocked.*click|kyc.*suspended.*update|pan.*card.*link)'
]

app_instance = None

if platform == 'android':
    from jnius import autoclass, PythonJavaClass, java_method
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    AudioManager = autoclass('android.media.AudioManager')
    ToneGenerator = autoclass('android.media.ToneGenerator')
    AlertDialogBuilder = autoclass('android.app.AlertDialog$Builder')
    IntentFilter = autoclass('android.content.IntentFilter')
    SmsMessage = autoclass('android.telephony.SmsMessage')
    PowerManager = autoclass('android.os.PowerManager')

    class RunnableWrapper(PythonJavaClass):
        __javainterfaces__ = ['java/lang/Runnable']
        def __init__(self, func):
            super().__init__()
            self.func = func
        @java_method('()V')
        def run(self):
            self.func()

    class SMSReceiver(PythonJavaClass):
        __javainterfaces__ = ['android/content/BroadcastReceiver']
        __javacontext__ = 'app'

        @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
        def onReceive(self, context, intent):
            try:
                action = intent.getAction()
                if action == "android.provider.Telephony.SMS_RECEIVED":
                    bundle = intent.getExtras()
                    if bundle:
                        pdus = bundle.get("pdus")
                        if pdus:
                            full_sms = ""
                            for pdu in pdus:
                                msg = SmsMessage.createFromPdu(pdu)
                                full_sms += msg.getMessageBody()
                            if full_sms and app_instance:
                                app_instance.on_auto_sms_received(full_sms)
            except Exception as e:
                print(f"SMS Receiver Error: {e}")

    def wake_up_screen():
        try:
            activity = PythonActivity.mActivity
            pm = activity.getSystemService(Context.POWER_SERVICE)
            wake_lock = pm.newWakeLock(
                PowerManager.SCREEN_BRIGHT_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP,
                "SharvaApp:AlertWakeLock"
            )
            wake_lock.acquire(3000)
        except Exception as e:
            print(f"WakeLock Error: {e}")

    def trigger_emergency_vibration():
        wake_up_screen()
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
        def _show():
            try:
                activity = PythonActivity.mActivity
                builder = AlertDialogBuilder(activity)
                builder.setTitle(title)
                builder.setMessage(message)
                builder.setCancelable(False)
                btn_txt = "నేను అర్థం చేసుకున్నాను (OK)" if is_danger else "సరే (OK)"
                builder.setPositiveButton(btn_txt, None)
                
                dialog = builder.create()
                dialog.setCanceledOnTouchOutside(False)
                dialog.show()
            except Exception as e:
                print(f"Flash Alert Error: {e}")

        activity = PythonActivity.mActivity
        activity.runOnUiThread(RunnableWrapper(_show))

else:
    def trigger_emergency_vibration():
        print("[Simulated] SIREN & VIBRATION TRIGGERED!")

    def show_government_flash_alert(title, message, is_danger=True):
        print(f"\n================ FLASH ALERT ================\n[ {title} ]\n{message}\n=============================================\n")

class SharvaApp(App):
    def build(self):
        global app_instance
        app_instance = self

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.title_label = Label(
            text="SHARVA CYBER DEFENSE\n[ EMERGENCY SECURITY SYSTEM ]",
            font_size='20sp',
            bold=True,
            line_height=1.4,
            size_hint_y=0.15,
            halign='center',
            valign='middle'
        )
        self.title_label.bind(size=lambda s, w: setattr(s, 'text_size', w))
        layout.add_widget(self.title_label)
        
        self.input_text = TextInput(
            hint_text="Waiting for incoming SMS or paste manually...",
            size_hint_y=0.35,
            multiline=True,
            font_size='16sp',
            line_spacing=4
        )
        layout.add_widget(self.input_text)
        
        self.scan_btn = Button(
            text="AI SCAN NOW",
            size_hint_y=0.12,
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            font_size='16sp'
        )
        self.scan_btn.bind(on_press=self.start_manual_scan)
        layout.add_widget(self.scan_btn)
        
        self.result_label = Label(
            text="SYSTEM READY\nBackground SMS Guardian Active",
            font_size='16sp',
            line_height=1.4,
            size_hint_y=0.38,
            bold=True,
            halign='center',
            valign='middle'
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
                ], self.register_background_receiver)
            except Exception as e:
                print(f"Permission error: {e}")

    def register_background_receiver(self, permissions, grant_results):
        try:
            activity = PythonActivity.mActivity
            self.sms_receiver = SMSReceiver()
            intent_filter = IntentFilter("android.provider.Telephony.SMS_RECEIVED")
            intent_filter.setPriority(999)
            activity.registerReceiver(self.sms_receiver, intent_filter)
        except Exception as e:
            print(f"Receiver Registration Error: {e}")

    @mainthread
    def on_auto_sms_received(self, text):
        self.input_text.text = text
        self.result_label.color = (1, 0.8, 0.2, 1)
        self.result_label.text = "NEW SMS INTERCEPTED!\nAI Analyzing in real-time..."
        threading.Thread(target=self.process_hybrid_ai, args=(text,)).start()

    def start_manual_scan(self, instance):
        text = self.input_text.text.strip()
        if not text:
            self.result_label.color = (1, 1, 1, 1)
            self.result_label.text = "Please enter SMS text!"
            return

        self.result_label.color = (1, 0.8, 0.2, 1)
        self.result_label.text = "ANALYZING SMS...\nPlease wait..."
        self.scan_btn.disabled = True

        threading.Thread(target=self.process_hybrid_ai, args=(text,)).start()

    def process_hybrid_ai(self, text):
        prompt = (
            f"Analyze this SMS: '{text}'. Detect scam/fraud or legitimate status. "
            "Reply strictly in natural Telugu within 2 lines. "
            "Start with [FRAUD] for scam or [SAFE] for genuine message."
        )

        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

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
                self.handle_ai_response(ai_text, mode="ONLINE AI")
                return
        except Exception as e:
            print(f"Online AI fallback: {e}")

        self.process_offline_ai(text)

    @mainthread
    def handle_ai_response(self, ai_reply, mode="ONLINE AI"):
        self.scan_btn.disabled = False
        is_fraud = "[FRAUD]" in ai_reply.upper() or "మోసం" in ai_reply or "ప్రమాదం" in ai_reply
        clean_telugu = ai_reply.replace("[FRAUD]", "").replace("[SAFE]", "").strip()

        if is_fraud:
            trigger_emergency_vibration()
            self.result_label.color = (1, 0.1, 0.1, 1)
            self.result_label.text = f"[ FRAUD DETECTED! ]\n({mode})"
            
            warning = (
                f"అత్యవసర సైబర్ భద్రతా హెచ్చరిక!\n\n"
                f"{clean_telugu}\n\n"
                f"సూచన: ఇందులో ఉన్న లింకులు నొక్కకండి, OTP పంచుకోవద్దు!"
            )
            show_government_flash_alert("⚠️️ సైబర్ మోసం గుర్తించబడింది!", warning, is_danger=True)
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = f"[ SAFE MESSAGE ]\n({mode})"
            show_government_flash_alert("సురక్షిత సందేశం", f"ఈ సందేశంలో ఎటువంటి ముప్పు లేదు.\n\n{clean_telugu}", is_danger=False)

    @mainthread
    def process_offline_ai(self, text):
        self.scan_btn.disabled = False
        lower_t = text.lower()
        is_fraud = any(re.search(pat, lower_t) for pat in CRITICAL_FRAUD_PATTERNS)

        if is_fraud:
            trigger_emergency_vibration()
            self.result_label.color = (1, 0.1, 0.1, 1)
            self.result_label.text = "[ FRAUD DETECTED! ]\n(OFFLINE AI)"
            
            offline_warning = (
                "అత్యవసర సైబర్ భద్రతా హెచ్చరిక! (ఆఫ్‌లైన్ రక్షణ)\n\n"
                "ఇందులో మోసపూరిత లింక్, నకిలీ ఏపీకే లేదా టెలిగ్రామ్ స్కామ్ వివరాలు ఉన్నాయి.\n\n"
                "మీ బ్యాంక్ ఖాతా లేదా వ్యక్తిగత సమాచారం చోరీకి గురయ్యే ప్రమాదం ఉంది. వెంటనే తిరస్కరించండి!"
            )
            show_government_flash_alert("⚠️️ అత్యవసర సైబర్ హెచ్చరిక!", offline_warning, is_danger=True)
        else:
            self.result_label.color = (0.1, 1, 0.1, 1)
            self.result_label.text = "[ SAFE MESSAGE ]\n(OFFLINE AI)"
            show_government_flash_alert("సురక్షిత సందేశం", "ఆఫ్‌లైన్ రక్షణ ప్రకారం ఈ సాధారణ లావాదేవీ సందేశంలో ఎటువంటి ముప్పు లేదు.", is_danger=False)

if __name__ == '__main__':
    SharvaApp().run()
