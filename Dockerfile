FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Criar as tabelas do banco de dados
RUN flask create_tables

EXPOSE 5000

CMD ["python", "app.py"]