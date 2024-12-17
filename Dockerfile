# Use an official Python runtime as a parent image for the bot part
FROM python:3.9-slim as bot

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Use the official nginx image for the web server part
FROM nginx:latest as nginx

# Copy our custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy over the Python bot into the nginx container for simplicity
COPY --from=bot /app /app

# Expose port 80 for Nginx
EXPOSE 80

# Run Nginx in the foreground and start the Python bot in the background
CMD ["sh", "-c", "nginx -g 'daemon off;' & python3 /app/main.py"]
