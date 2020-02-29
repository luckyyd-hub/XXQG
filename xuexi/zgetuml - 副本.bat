@echo off
cd /d %~dp0
echo 连接Android。。。
adb connect 127.0.0.1:7555
adb shell input swipe 200 200 500 200 1000
pause