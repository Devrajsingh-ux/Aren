@echo off
echo Initializing A.R.E.N...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

:: Run A.R.E.N
echo Starting A.R.E.N...
python main.py
if errorlevel 1 (
    echo A.R.E.N encountered an error. Please check the logs for details.
    pause
    exit /b 1
)

:: Deactivate virtual environment
call venv\Scripts\deactivate

pause 