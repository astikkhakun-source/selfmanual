FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for WeasyPrint/ReportLab & font rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgobject-2.0-0 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    fontconfig \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Default command runs the bot (or fastAPI via docker-compose)
CMD ["python", "run_bot.py"]
