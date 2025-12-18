#!/bin/bash
# Quick launch script for Multi-Timer Application

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./install.sh first."
    exit 1
fi

source venv/bin/activate
python3 timer_app/main.py
