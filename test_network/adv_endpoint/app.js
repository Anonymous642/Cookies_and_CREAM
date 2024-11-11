const bodyParser = require("body-parser");
const express = require("express");
const fs = require("fs");
const http = require("http");
const https = require("https");
const request = require("request");

const app = express();

https.createServer({key: fs.readFileSync("server.key"),
                    cert: fs.readFileSync("server.crt")},
                    app).listen(443, () => {console.log("HTTPS server started")});
                    
http.createServer(app).listen(80, () => {console.log("HTTP server started")});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

app.all("/", (req, resp) => {
    console.log(req.body);
    resp.send("Big McThankies from McSpankies");
    });
