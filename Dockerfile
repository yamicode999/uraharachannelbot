# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY configs.py .
COPY urahara.py .

# Define environment variable for Telegram bot token (you'll need to set this when running the container)
ENV TELEGRAM_BOT_TOKEN=your_bot_token_here

# Run mybot.py when the container launches
CMD ["python", "urahara.py"]
