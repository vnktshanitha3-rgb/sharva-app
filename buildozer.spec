[app]
title = Sharva App
package.name = sharvaapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Automatic SMS detection, Emergency Vibration mariyu Notification permissions
android.permissions = RECEIVE_SMS, READ_SMS, VIBRATE, POST_NOTIFICATIONS

[buildozer]
log_level = 2
warn_on_root = 1
