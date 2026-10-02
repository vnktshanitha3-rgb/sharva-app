[app]
title = Sharva App
package.name = sharvaapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# Gemini AI API ని ఇంటర్నెట్ ద్వారా కనెక్ట్ చేయడానికి అవసరమైన ప్యాకేజీలు
requirements = python3,kivy,pyjnius,openssl,urllib3,certifi

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# SMS, Vibration తో పాటు Gemini AI కోసం తప్పనిసరిగా INTERNET పర్మిషన్ చేర్చాం
android.permissions = RECEIVE_SMS, READ_SMS, VIBRATE, POST_NOTIFICATIONS, INTERNET, ACCESS_NETWORK_STATE

[buildozer]
log_level = 2
warn_on_root = 1
