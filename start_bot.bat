@echo off
echo Starting Discord Music Bot...
echo.
echo Make sure you have:
echo 1. Created a .env file with your DISCORD_TOKEN
echo 2. Installed all requirements (pip install -r requirements.txt)
echo 3. Installed FFmpeg and added it to PATH
echo.
echo Press any key to continue...
pause >nul

python main.py

echo.
echo Bot has stopped. Press any key to exit...
pause >nul
