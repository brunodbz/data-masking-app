FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Não criamos as tabelas aqui, vamos fazer isso no entrypoint
CMD ["python", "app.py"]