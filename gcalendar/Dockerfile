# Základní obraz s Pythonem
FROM python:3.11-slim

# Nastavení pracovní složky
WORKDIR /app

# Instalace požadavků
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Zkopírování celého projektu
COPY . .

# Nastavíme spustitelnost skriptu
RUN chmod +x /run.sh

# Výchozí příkaz (spouští vše)
CMD ["/run.sh"]
