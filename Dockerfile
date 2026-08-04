FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_FILE=/data/data.json

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Directory for the persisted data volume (data.json lives here)
RUN mkdir -p /data

# Seed data.json from the example on first start if it is missing,
# then run the bot.
CMD ["sh", "-c", "if [ ! -f \"$DATA_FILE\" ] && [ -f example_data.json ]; then cp example_data.json \"$DATA_FILE\"; fi; python bot.py"]
