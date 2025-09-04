FROM python:3.13-slim

# Install Chromium and Chromedriver
RUN apt-get update && apt-get install -y chromium chromium-driver && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY scraper_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper code
COPY scraper_worker/ .

# Run scraper
CMD ["python", "scraper.py"]
