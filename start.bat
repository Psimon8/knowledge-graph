@echo off
REM Knowledge Graph Explorer - Quick Start Script for Windows
REM This script helps you set up and run the application quickly

echo.
echo 🕸️  Knowledge Graph Explorer - Setup
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Creating .env from .env.example...
    
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ .env file created
        echo.
        echo 📝 IMPORTANT: Edit the .env file and add your OpenAI API key!
        echo    Open .env in a text editor and replace 'your_openai_api_key_here'
        echo    with your actual API key from https://platform.openai.com/api-keys
        echo.
        pause
    ) else (
        echo ❌ .env.example not found. Creating minimal .env...
        echo OPENAI_API_KEY=your_openai_api_key_here > .env
        echo ⚠️  Please edit .env and add your OpenAI API key!
        pause
        exit /b 1
    )
) else (
    echo ✅ .env file found
)
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.

REM Run the application
echo 🚀 Starting Knowledge Graph Explorer...
echo The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py
