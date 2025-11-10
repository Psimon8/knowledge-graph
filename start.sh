#!/bin/bash

# Knowledge Graph Explorer - Quick Start Script
# This script helps you set up and run the application quickly

echo "🕸️  Knowledge Graph Explorer - Setup"
echo "====================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "📝 IMPORTANT: Edit the .env file and add your OpenAI API key!"
        echo "   Open .env in a text editor and replace 'your_openai_api_key_here'"
        echo "   with your actual API key from https://platform.openai.com/api-keys"
        echo ""
        read -p "Press Enter when you've added your API key..."
    else
        echo "❌ .env.example not found. Creating minimal .env..."
        echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
        echo "⚠️  Please edit .env and add your OpenAI API key!"
        exit 1
    fi
else
    echo "✅ .env file found"
fi
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Run the application
echo "🚀 Starting Knowledge Graph Explorer..."
echo "The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
