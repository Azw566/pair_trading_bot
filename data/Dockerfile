FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances
RUN pip install --no-cache-dir ccxt pandas

# Copie du script dans le conteneur
COPY fetch_binance_ohlcv.py .

# Création du dossier qui recevra les CSV
RUN mkdir data

# Commande de lancement
CMD ["python", "fetch_binance_ohlcv.py"]