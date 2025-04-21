# Základní obraz s Pythonem
FROM python:3.11-slim

# Nastavení pracovní složky
WORKDIR /app

# Instalace potřebných knihoven
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Zkopírování celého projektu
COPY . .

# Oprávnění pro spustitelný skript (pokud používáš run.sh)
RUN chmod +x /app/run.sh

# Spuštění aplikace (spustíme přímo app.py z backend/)
CMD ["python3", "backend/app.py"]
