# Use a Python image with more development tools
FROM python:3.9 as bot

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for TgCrypto
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Use Nginx for the final image
FROM nginx:latest

# Install Python 3 in the Nginx image along with build essentials for TgCrypto
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    libssl-dev \
    gcc \
    python3-dev \
    g++ \
    libffi-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for Python packages
RUN mkdir -p /app

# Copy Python application files
COPY --from=bot /app /app

# Copy Python site-packages
COPY --from=bot /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy our custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for Nginx
EXPOSE 8080

# Set Python path to ensure Python can find the installed packages
ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages

# Run Nginx in the foreground and start the Python bot in the background
CMD ["sh", "-c", "nginx -g 'daemon off;' & python3 /app/main.py"]
