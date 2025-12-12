@echo off
chcp 65001 >nul
color 0B

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗          ║
echo ║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝          ║
echo ║        ██║███████║██████╔╝██║   ██║██║███████╗          ║
echo ║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║          ║
echo ║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║          ║
echo ║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝          ║
echo ║                                                           ║
echo ║              U L T I M A T E   E D I T I O N              ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Active l'environnement virtuel
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Environnement virtuel activé
) else (
    echo ⚠️  Environnement virtuel non trouvé
    echo Lance d'abord INSTALL_ULTIMATE.bat
    pause
    exit /b 1
)

echo.
echo 🚀 Lancement de JARVIS ULTIMATE...
echo.
echo 💡 CONSEILS :
echo    • Interface web : http://localhost:5000
echo    • Dis "Jarvis" avant chaque commande
echo    • Dis "Jarvis aide" pour voir les commandes
echo    • Ctrl+C pour quitter
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM Lance Jarvis
python main_ultimate.py

REM Si crash
if errorlevel 1 (
    echo.
    echo ❌ JARVIS s'est arrêté avec une erreur
    echo.
    pause
)

echo.
echo 👋 À bientôt !
timeout /t 3 >nul