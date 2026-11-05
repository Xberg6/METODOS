@echo off
setlocal
cd /d "%~dp0"
if exist ".entorno\Scripts\python.exe" goto instalar
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
  py -3.12 -m venv .entorno
  goto comprobar
)
py -3 --version >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .entorno
  goto comprobar
)
python --version >nul 2>&1
if not errorlevel 1 (
  python -m venv .entorno
  goto comprobar
)
echo Instale Python 3.12 desde https://www.python.org/downloads/ y marque Add Python to PATH.
goto fallo
:comprobar
if errorlevel 1 goto fallo
if not exist ".entorno\Scripts\python.exe" goto fallo
:instalar
".entorno\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 'Se necesita Python 3.11 o posterior. Se recomienda 3.12.')"
if errorlevel 1 goto fallo
".entorno\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fallo
echo Instalacion completada. Abra Abrir_simulador.cmd para iniciar.
pause
exit /b 0
:fallo
echo No se completo la instalacion. Revise el mensaje anterior y el README.
pause
exit /b 1
