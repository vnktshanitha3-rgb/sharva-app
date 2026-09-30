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

# Modern 64-bit phones only (prevents memory crash and cuts build time)
android.archs = arm64-v8a

[buildozer]
# Low log level to prevent GitHub log truncation
log_level = 1
warn_on_root = 1

[buildozer:android]
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.accept_sdk_license = True
android.permissions = INTERNET
