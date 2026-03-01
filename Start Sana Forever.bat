@echo off
cd /d %~dp0
call venv\Scripts\activate
python "Sana Forever.py"
pause