[app]
title = Sharva App
package.name = sharvaapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# Gemini AI mariyu Android Native calls kosam avasaramaina packages
requirements = python3,kivy,pyjnius,openssl,urllib3,certifi

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Automatic SMS detection, Full-screen Flash Alert & Siren kosam avasaramaina permissions
android.permissions = RECEIVE_SMS, READ_SMS, VIBRATE, POST_NOTIFICATIONS, INTERNET, ACCESS_NETWORK_STATE, SYSTEM_ALERT_WINDOW, WAKE_LOCK, FOREGROUND_SERVICE

[buildozer]
log_level = 2
warn_on_root = 1
