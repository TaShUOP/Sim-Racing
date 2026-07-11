FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose HTTP API port
EXPOSE 1224
# Expose UDP telemetry port
EXPOSE 20777/udp

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "1224"]
