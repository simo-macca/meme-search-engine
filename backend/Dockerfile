FROM python:3.12-slim

WORKDIR /app

# Install OS dependencies required by Playwright
RUN apt-get update && apt-get install -y wget gnupg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .

# Run the automated orchestrator
CMD ["python", "main.py"]