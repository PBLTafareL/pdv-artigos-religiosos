@echo off
title Flor de Dende PDV - Instalacao
color 0A
echo.
echo  ==========================================
echo   Flor de Dende PDV - Instalacao
echo  ==========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! Instale em python.org
    pause & exit /b 1
)
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado! Instale em nodejs.org
    pause & exit /b 1
)
echo [OK] Python e Node.js encontrados.
echo.

cd /d "%~dp0backend"

echo [1/4] Criando ambiente virtual...
if not exist venv (
    python -m venv venv
)

echo [2/4] Instalando dependencias Python...
call venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias. Veja o erro acima.
    pause & exit /b 1
)

echo [3/4] Criando migrations e banco...
python manage.py makemigrations accounts
python manage.py makemigrations products
python manage.py makemigrations pdv
python manage.py makemigrations quotations
python manage.py makemigrations invoices
python manage.py makemigrations loyalty
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERRO] Falha nas migrations. Verifique se o MySQL esta rodando e o banco foi criado.
    pause & exit /b 1
)

echo [4/4] Instalando dependencias frontend...
cd /d "%~dp0frontend"
npm install

echo.
echo  ==========================================
echo   Instalacao concluida com sucesso!
echo  ==========================================
echo.
echo Deseja criar o superusuario agora? (S/N)
set /p resp=
if /i "%resp%"=="S" (
    cd /d "%~dp0backend"
    call venv\Scripts\activate.bat
    python manage.py createsuperuser
)
echo.
echo Agora execute: iniciar.bat
pause
