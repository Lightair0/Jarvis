@echo off
chcp 65001 >nul
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║     JARVIS ULTIMATE - Installation Automatique           ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Vérifie Python
echo [1/6] 🔍 Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé !
    echo Télécharge Python 3.10+ sur https://python.org
    pause
    exit /b 1
)
echo ✅ Python détecté

REM Crée l'environnement virtuel
echo.
echo [2/6] 📦 Création de l'environnement virtuel...
if not exist "venv" (
    python -m venv venv
    echo ✅ Environnement virtuel créé
) else (
    echo ⚠️  Environnement virtuel déjà existant
)

REM Active l'environnement
echo.
echo [3/6] ⚡ Activation de l'environnement...
call venv\Scripts\activate.bat

REM Installe les dépendances
echo.
echo [4/6] 📥 Installation des dépendances (ça peut prendre 2-3 min)...
pip install --upgrade pip >nul 2>&1
pip install -r requirements_ultimate.txt

if errorlevel 1 (
    echo ⚠️  Certaines dépendances ont échoué, mais on continue...
) else (
    echo ✅ Toutes les dépendances installées
)

REM Crée le dossier skills s'il n'existe pas
echo.
echo [5/6] 📁 Vérification de la structure...
if not exist "skills" mkdir skills
if not exist "skills\__init__.py" echo. > skills\__init__.py
echo ✅ Structure OK

REM Vérifie les fichiers essentiels
echo.
echo [6/6] 🔍 Vérification des fichiers...
set MISSING=0

if not exist "main_ultimate.py" (
    echo ❌ main_ultimate.py manquant
    set MISSING=1
)
if not exist "assistant_ultimate.py" (
    echo ❌ assistant_ultimate.py manquant
    set MISSING=1
)
if not exist "speech.py" (
    echo ❌ speech.py manquant
    set MISSING=1
)
if not exist "listener.py" (
    echo ❌ listener.py manquant
    set MISSING=1
)

if %MISSING%==1 (
    echo.
    echo ⚠️  Certains fichiers sont manquants !
    echo Assure-toi d'avoir tous les fichiers du projet.
    pause
    exit /b 1
)

echo ✅ Tous les fichiers présents

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   ✨ INSTALLATION TERMINÉE AVEC SUCCÈS ! ✨               ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🚀 Pour lancer JARVIS ULTIMATE :
echo    1. Double-clique sur LAUNCH_JARVIS.bat
echo    OU
echo    2. Tape : python main_ultimate.py
echo.
echo 🌐 Interface web : http://localhost:5000
echo.
echo 📖 Lis le README_ULTIMATE.md pour plus d'infos
echo.
pause