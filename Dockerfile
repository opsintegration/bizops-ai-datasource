# Use the official Python slim image
FROM python:3.11-slim-bullseye

# Set the working directory
WORKDIR /app

# Install system dependencies for Node.js, curl, Playwright, PostgreSQL client, ping, and DNS utilities
RUN apt-get update && \
    apt-get install -y curl gnupg2 ca-certificates postgresql-client iputils-ping dnsutils vim && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js and npm using NodeSource repository
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Verify the installation of node and npm
RUN node -v && npm -v

# Install Playwright and additional system dependencies for running browsers
RUN npm install -g playwright && \
    apt-get update && \
    apt-get install -y \
        libnss3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libcups2 \
        libxss1 \
        libgdk-pixbuf2.0-0 \
        libgtk-3-0 \
        libasound2 \
        fonts-liberation \
        libjpeg62-turbo \
        libenchant-2-2 \
        libicu67 \
        libvpx6 \
        libevent-2.1-7

# Install Playwright browsers
RUN PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright/ playwright install --with-deps

# Copy the rest of the application code
COPY src/ ./src/
COPY creds.env .

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Load environment variables from creds.env
RUN export $(grep -v '^#' creds.env | xargs)

# Set the entrypoint to the script
ENTRYPOINT ["/app/entrypoint.sh"]

# Set the command to run your application
CMD ["python", "src/main.py"]
