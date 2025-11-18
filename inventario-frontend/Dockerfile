# Multi-stage Dockerfile: build frontend with Node, serve with nginx
FROM node:18-alpine AS build
WORKDIR /app
# Copy all frontend files (this Dockerfile will be used with build context = inventario-frontend)
COPY . .
RUN npm ci --silent
RUN npm run build:mobile

FROM nginx:stable-alpine AS release
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

