@echo off
echo Activating virtual environment...
call venv\Scripts\activate

echo Starting the Telegram bot...
python main.py

echo Bot has stopped.
pause
