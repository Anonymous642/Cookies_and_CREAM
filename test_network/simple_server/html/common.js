const __directory = "/home/node/app/";  // The directory everything is located in in the container
const https = require("https");
const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");;


// Web Server Setup
const app = express();

// Create the https server
https.createServer({key: fs.readFileSync("asym.key"), 
                    cert: fs.readFileSync("asym.crt"),
                    },
                    app).listen(443, () => {console.log("server started")});

// Add the middleware to read the requests body and cookies
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));
app.use(cookieParser())

app.get("/", (req, res) => {
    //res.cookie("test", "test",{httpOnly:true});
    //res.cookie("test_browserOnly", "test",{browserOnly:true});
    res.cookie("test_monitored", "test",{monitored: {level:"high", message:"test one"}});
    res.send("Thanks for playing")
});
