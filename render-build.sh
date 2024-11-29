#!/usr/bin/env bash
# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb
# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oP '\d{2,3}' | head -n 1)
wget https://chromedriver.storage.googleapis.com/$CHROME_VERSION.0/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/
