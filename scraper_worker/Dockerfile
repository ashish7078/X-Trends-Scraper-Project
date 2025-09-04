FROM python:3.13-slim

# Install system dependencies (Chromium + basic tools)
RUN apt-get update && apt-get install -y \
    wget \
    chromium \
    fonts-liberation \
    libnss3 \
    libasound2 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Tell undetected-chromedriver where Chromium is
ENV CHROME_BIN=/usr/bin/chromium

# Set working directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start scraper
CMD ["python", "scraper_worker/scraper.py"]
