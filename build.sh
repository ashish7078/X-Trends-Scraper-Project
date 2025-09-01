#!/bin/bash

# Exit script on any error
set -e

# 1. Build the React Frontend
echo ">>> Building React frontend..."
cd xtrends_frontend
npm install
npm run build
cd ..

# 2. Install Python Dependencies
# (Installs from the requirements.txt file in your root directory)
echo ">>> Installing Python backend dependencies..."
pip install -r requirements.txt

# 3. Move Django project to the root
# This is necessary for Vercel's Python runtime to find your wsgi.py
echo ">>> Moving backend files to root..."
mv api/* .