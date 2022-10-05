### Dockerfile
FROM node:15.12.0-alpine3.13 as builder

# make the 'app' folder the current working directory
WORKDIR /app

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json \
     babel.config.js \
     vue.config.js \
     docker/frontend/nginx.default.conf ./

# install project dependencies
RUN npm install

COPY src/ src/
COPY public/ public/

# run build
RUN npm run build


FROM nginx:1.19.9-alpine

WORKDIR /app

COPY --from=builder /app/nginx.default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /app/dist

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]