FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (for better caching)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    discord.py>=2.0.0 \
    google-api-python-client>=2.0.0 \
    google-auth>=2.0.0 \
    google-auth-oauthlib>=0.5.0 \
    google-auth-httplib2>=0.1.0 \
    python-dotenv>=1.0.0

# Copy the source code
COPY src/ ./src/
COPY bot.py ./

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash ctfbot
USER ctfbot

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command
CMD ["python", "bot.py"]