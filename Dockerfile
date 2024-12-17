# Stage 1: Build and prepare the Python bot
FROM python:3.9-slim as bot

# Set the working directory
WORKDIR /app

# Install system dependencies required for TgCrypto and Python builds
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production-ready image with Nginx and Python runtime
FROM nginx:stable-slim

# Set the working directory
WORKDIR /app

# Install Python 3 and necessary dependencies in the Nginx image
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python bot and dependencies from the build stage
COPY --from=bot /app /app
COPY --from=bot /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for Nginx
EXPOSE 80

# Start Nginx and Python bot together
CMD ["sh", "-c", "python3 /app/main.py & nginx -g 'daemon off;'"]
