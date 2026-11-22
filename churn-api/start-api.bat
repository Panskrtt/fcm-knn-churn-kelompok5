@echo off
REM Menjalankan API Python (FastAPI) di Windows. Jalankan dengan klik dua kali atau dari terminal.
cd /d %~dp0
if not exist venv ( python -m venv venv )
call venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8001
