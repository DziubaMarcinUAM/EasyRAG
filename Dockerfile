FROM python:3.11-slim
WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y gcc g++ build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Source Code
COPY . .

# Default command (starts the bot)
CMD ["python", "app.py"]