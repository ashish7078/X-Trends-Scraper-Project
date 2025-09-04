FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies and Chrome + ChromeDriver
RUN apt-get update && apt-get install -y wget unzip gnupg curl \
 && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update && apt-get install -y google-chrome-stable \
 \
 # Get Chrome major version
 && CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
 \
 # Fetch latest compatible driver
 && DRIVER_VERSION=$(wget -qO- "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION") \
 \
 # Download and install ChromeDriver
 && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$DRIVER_VERSION/linux64/chromedriver-linux64.zip" \
 && unzip chromedriver-linux64.zip -d /usr/local/bin/ \
 && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
 && rm -rf chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64 \
 \
 # Cleanup
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the scraper
CMD ["python", "scraper.py"]
