# backend/Dockerfile

# Usa Python leggero
FROM python:3.9-slim

# Cartella di lavoro dentro il container
WORKDIR /app

# Installa librerie di sistema (Aggiornato per Debian recente)
# Abbiamo sostituito 'libgl1-mesa-glx' con 'libgl1'
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia i requisiti e installali
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del backend
COPY . .

# Apre la porta 8000
EXPOSE 8000

# Avvia il server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]