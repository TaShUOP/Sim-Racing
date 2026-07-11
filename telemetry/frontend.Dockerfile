FROM node:18-alpine AS build
WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Update Nginx to listen on the requested port 1223
RUN sed -i 's/listen  *80;/listen 1223;/g' /etc/nginx/conf.d/default.conf

EXPOSE 1223
CMD ["nginx", "-g", "daemon off;"]
