@echo off
rem Gera dist\ReciboPix.exe e (se o Inno Setup estiver instalado) o instalador.
pip install -r requirements.txt pyinstaller || exit /b 1
pyinstaller --noconfirm --onefile --windowed --name ReciboPix main.py || exit /b 1
set APP_VERSION=1.0.0
where iscc >nul 2>nul && iscc installer\ReciboPix.iss
echo Pronto. Veja a pasta dist\ e dist-installer\
