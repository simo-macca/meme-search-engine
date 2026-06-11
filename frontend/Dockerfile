# Build Stage
FROM node:20-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# We set VITE_SOLR_PATH to empty so Axios calls /solr/... (handled by Nginx Proxy)
ENV VITE_SOLR_PATH=""
RUN npm run build

# Production Stage
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]