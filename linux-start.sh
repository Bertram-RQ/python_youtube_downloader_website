#!/bin/bash

set -e

echo "==> Detecting package manager..."

# Detect and set the package manager
if command -v apt &> /dev/null; then
    PKG="apt"
    UPDATE="apt update"
    INSTALL="apt install -y"
elif command -v dnf &> /dev/null; then
    PKG="dnf"
    UPDATE="dnf check-update || true"
    INSTALL="dnf install -y"
elif command -v pacman &> /dev/null; then
    PKG="pacman"
    UPDATE="pacman -Sy"
    INSTALL="pacman -S --noconfirm"
else
    echo "Unsupported Linux distribution."
    exit 1
fi

echo "==> Using package manager: $PKG"
eval "$UPDATE"

echo "==> Installing Python, pip, and FFmpeg..."
case "$PKG" in
    apt)
        $INSTALL python3 python3-pip ffmpeg
        PYTHON=python3
        ;;
    dnf)
        $INSTALL python3 python3-pip ffmpeg
        PYTHON=python3
        ;;
    pacman)
        $INSTALL python python-pip ffmpeg
        PYTHON=python
        ;;
esac

echo "==> Creating virtual environment..."
$PYTHON -m venv venv

# Arch-specific fix for PEP 668
if [[ "$PKG" == "pacman" ]]; then
    echo "==> Removing 'externally-managed' restriction (Arch-specific)..."
    rm -f venv/lib/python*/externally-managed || true
fi

echo "==> Activating virtual environment..."
source venv/bin/activate

echo "==> Installing requirements..."
pip install -r requirements.txt -U

echo "==> Starting program..."
$PYTHON ./website/python_website.py
