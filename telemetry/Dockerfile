# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Final image with Python, Nginx, Supervisor
FROM python:3.11-slim

# Install nginx and supervisor
RUN apt-get update && \
    apt-get install -y nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Configure Nginx for frontend
COPY --from=frontend-build /app/dist /usr/share/nginx/html
# Update nginx to listen on port 1223 instead of 80
RUN sed -i 's/listen  *80;/listen 1223;/g' /etc/nginx/conf.d/default.conf

# Setup supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
# 1223: Frontend (Nginx)
# 1224: Backend API (Uvicorn)
# 20777/udp: F1 25 Telemetry UDP
EXPOSE 1223 1224 20777/udp

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
