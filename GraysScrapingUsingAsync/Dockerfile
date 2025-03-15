# Use Playwright base image with Python
FROM mcr.microsoft.com/playwright/python:v1.39.0-focal

# Set working directory
WORKDIR /app

# Install system dependencies and Google Chrome using the new keyring method
RUN apt-get update && apt-get install -y wget unzip curl gnupg && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-linux-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Copy the entire project into the container
COPY . .

# Set default command to run both scripts sequentially
CMD ["bash", "-c", "python collect_links.py && python Async_Scraping.py"]
