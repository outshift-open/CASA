FROM node:22-alpine3.22 AS build

# Install packages
RUN apk add --update \
  libpng-dev \
  build-base \
  nodejs \
  npm \
  yarn

# Set workdir
WORKDIR /home/web

# Copy src
COPY ./demo/demo-ui .

# Install libs
RUN yarn install
RUN yarn build

FROM alpine:3.22

# Install packages
RUN apk add --update \
  gettext \
  nginx

# Create a group and user
RUN addgroup -S web && adduser -S -G web -u 999 web

# Set workdir
WORKDIR /home/web

COPY --from=build /home/web/dist ./dist
COPY --chown=web:web ./deployments/docker/demo/frontend/nginx.conf ./nginx/nginx.conf
RUN mkdir ./nginx/logs && \
  mkdir ./nginx/tmp && \
  chown web:web ./nginx/logs && \
  chown web:web ./nginx/tmp

# Set non root user
USER web

CMD ["/usr/sbin/nginx", "-c", "/home/web/nginx/nginx.conf", "-g", "daemon off;pid /home/web/nginx/nginx.pid;", "-p", "/home/web/nginx"]