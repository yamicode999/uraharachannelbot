# Use Python as the base image for the bot part
FROM python:3.9-slim as bot

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Use Nginx as the final image
FROM nginx:latest

# Copy over the Python bot code
COPY --from=bot /app /app

# Install Python 3 in the Nginx image
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Copy our custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for Nginx
EXPOSE 80

# Run Nginx in the foreground and start the Python bot in the background
CMD ["sh", "-c", "nginx -g 'daemon off;' & python3 /app/main.py"]
