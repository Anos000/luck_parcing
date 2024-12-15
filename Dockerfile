FROM python:3.10-slim

# Install dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg2 \
    ca-certificates \
    unzip \
    libx11-xcb1 \
    libgl1-mesa-glx \
    libgtk-3-0 \
    libxcomposite1 \
    libxrandr2 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome.deb && \
    dpkg -i google-chrome.deb; \
    apt-get -y install -f; \
    rm google-chrome.deb

# Install required Python packages
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Chrome
ENV CHROME_BIN="/usr/bin/google-chrome-stable"
