@echo off
cd /d %~dp0
echo Let's Go!
venv\scripts\python -m xuexi -a -c -d -v
pause