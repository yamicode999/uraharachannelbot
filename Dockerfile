# Use a Python image to get Python 3.9
FROM python:3.9-slim as python-runtime

# Use Nginx for the final image
FROM nginx:latest

# Update system packages and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy Python 3.9 from our Python runtime image
COPY --from=python-runtime /usr/local/bin/python3.9 /usr/local/bin/python3.9
COPY --from=python-runtime /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=python-runtime /usr/local/lib/libpython3.9.so* /usr/local/lib/
COPY --from=python-runtime /usr/local/bin/pip3 /usr/local/bin/pip3

# Adjust library path
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Create symbolic links for 'python3' and 'pip3' if needed, but only if they don't exist
RUN if [ ! -e /usr/local/bin/python3 ]; then ln -s /usr/local/bin/python3.9 /usr/local/bin/python3; fi
RUN if [ ! -e /usr/bin/python3 ]; then ln -s /usr/local/bin/python3.9 /usr/bin/python3; fi
RUN if [ ! -e /usr/local/bin/pip3 ]; then ln -s /usr/local/bin/pip3 /usr/local/bin/pip3; fi

# Verify Python installation
RUN python3 --version
RUN pip3 --version

# Set Python path to ensure Python can find the installed packages
ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages

# Rest of your Dockerfile setup here
# ... (your existing COPY commands, etc.)

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy our custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for Nginx
EXPOSE 8080

# Run Nginx in the foreground and start the Python bot in the background
CMD ["sh", "-c", "nginx -g 'daemon off;' & python3 /app/main.py"]
