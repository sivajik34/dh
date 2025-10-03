FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

EXPOSE 8005

CMD ["uvicorn", "order_service:app", "--host", "0.0.0.0", "--port", "8005"]
