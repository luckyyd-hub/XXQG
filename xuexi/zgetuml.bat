@echo off
cd /d %~dp0
echo 连接Android。。。
adb connect 127.0.0.1:7555
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml D:\ProgramFiles\xuexiqiangguo\AutoXue-master\xuexi\aui.xml
pause