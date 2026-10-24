FROM node:latest

WORKDIR /home/node/app
RUN npm install body-parser
RUN npm install express
RUN npm install request
COPY package.json /home/node/app/package.json
COPY app.js /home/node/app/app.js
COPY server.key /home/node/app/server.key
COPY server.crt /home/node/app/server.crt

EXPOSE 80
EXPOSE 443
