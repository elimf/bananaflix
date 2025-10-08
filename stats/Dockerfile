FROM python:3.9.6-slim

WORKDIR /app

# Copier les dépendances
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
