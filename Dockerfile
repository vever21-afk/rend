
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

COPY . .

# Render provides PORT env var
CMD ["python", "app.py"]
