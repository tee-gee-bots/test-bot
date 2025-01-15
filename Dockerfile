# Use Python 3.9 slim image 
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ .

# Set Python to run in unbuffered mode (recommended for logging in containers)
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot.py"]
