FROM node:latest

WORKDIR /home/node/app
RUN npm install express@4.18.3
RUN npm install body-parser
RUN npm install https://github.com/Anonymous642/CREAM_Node_fork.git
RUN npm install cookie-parser
RUN npm install mysql2
RUN npm install uuid

COPY ./html/  /home/node/app/
COPY asym.crt /home/node/app/
COPY asym.key /home/node/app/

EXPOSE 443
