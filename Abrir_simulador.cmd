@echo off
setlocal
cd /d "%~dp0"
if exist ".entorno\Scripts\python.exe" (
  ".entorno\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.headless false
  if errorlevel 1 pause
  exit /b
)
echo Primero ejecute Instalar_dependencias.cmd o siga los comandos del README.
pause
