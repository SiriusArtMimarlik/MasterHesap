[app]
title = MasterHesap
package.name = masterhesap
package.domain = org.siriusart
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow
presplash.filename = intro.png
icon.filename = logo.png
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1