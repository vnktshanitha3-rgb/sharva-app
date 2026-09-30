[app]
title = SHARVA
package.name = sharva
package.domain = org.sharva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[buildozer:android]
android.api = 34
android.minapi = 26
android.ndk_api = 26
android.accept_sdk_license = True
android.permissions = INTERNET
