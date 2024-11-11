const __directory = "/home/node/app/";  // The directory everything is located in in the container
const https = require("https");
const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");
const crypto = require('crypto');
const mysql = require('mysql2');

// Database Setup
var database;

/**
*  Opens a connection to the SQL databases loacted on the container at 172.20.0.2
*/
function connectDB(){
    database = mysql.createConnection({
        host: '172.20.0.2',
        port: 3306,
        database: 'web_server',
        user: 'server',
        password: 'server_pass'
    });
}

/**
*  Cleanly closes the connection with the database. Not vital for the actual website functionality.
*      As such closing is allowed asynchronously. Similarly if an error occurs we simply log it as 
*      larger issues with the databse will be caught by other error cases. 
*/
function disconnectDB(database){
    database.end(function(err){
        if(err){
            console.error("Error closing connection to the database: " + err.stack);
        }
    });
}

/** 
*  A template of the homepage displayed to the user after logging in. Kept as a string rather than  
*      in an html file for easier customization.
*/
const homePage = '<!DOCTYPE HTML><html><head><title>Holy cow you got in</title></head><body><div id="logoutButton"><a id="logout" href="/logout">Logout</a></div><div id="status"><p>Welcome <span style="color: COLOR">FIRSTNAME LASTNAME</span>...</p><p>I\'m not sure what you\'re looking for. There is nothing here.</div></body></html>'

// Cryptography Setup
const IV = crypto.randomBytes(16)
const secretKey = crypto.randomBytes(32)

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


/**
*  A function to invalidate the session token and redirect the user back to the landing page.
*    Essentially the result of any errors
*/
function invalidateCookie(token, res){
    // Invalidate our copy
    database.query("DELETE FROM sessions WHERE session_id=?", [token], function(err){
        if(err){
            console.error("Error deleting from sessions: " + err.stack);
        }
        disconnectDB(database);
        // Invalidate the browser's copy of the cookie
        res.cookie("Sess-Token", token, {maxAge: -1000000000000});
        res.redirect("/");
    });
}


/**
*  A function to validate any changes made to the cookie. Currently we simply
*    ensure the cookie wasn't changed at all, however, this can be modified to allow
*    some desired changes.
*/
function validateChangelog(changelog){
    return changelog.length == 0;
}


/**
*  A function to validate the cookies current configuration. We simply check that 
*    all the setting in the expected values saved configuration matches the current
*    configuration. This prevents an attacker from bypassing the change log by evicting the
*    cookie and making a new one.
*/
function validateCurrent(current, original){
    //console.log(original)
    //console.log(current)
    for(var setting in original){
        // Since the expires time will have slight wiggle due to latency, we ignore it
        //console.log(setting + ":" + original[setting] == current[setting]);
        if(setting == "E"){
            continue;
        }else if(!(original[setting] == current[setting])){
            return false;
        }
    }
    return true;
}

function convertSettings(settings){
    expandedSettings = {}
    for(var setting in settings){
        if(setting == "D"){
            expandedSettings.domain = settings.D;
        }else if(setting == "P"){
            expandedSettings.path = settings.P;
        }else if(setting == "E"){
            expandedSettings.expires = settings.E
        }else if(setting == "S"){
            if(settings.S){
                expandedSettings.secure = true
            }else{
                expandedSettings.secure = false
            }
        }else if(setting == "H"){
            if(settings.H){
                expandedSettings.httpOnly = true
            }else{
                expandedSettings.httpOnly = false
            }
        }else if(setting == "B"){
            if(settings.B){
                expandedSettings.browserOnly = true
            }else{
                expandedSettings.browserOnly = false
            }
        }else if(setting == "PT"){
            if(settings.PT){
                expandedSettings.partition = true
            }else{
                expandedSettings.partition = false
            }
        }else if(setting == "SS"){
            if(settings.SS == 0){
                expandedSettings.sameSite = "none";
            }else if(settings.SS == 1){
                expandedSettings.sameSite = "lax";
            }else if(settings.SS == 2){
                expandedSettings.sameSite = "strict";
            }
        }
    }
    return expandedSettings;
}

/**
*  A function to create the monitored cookie. This function allows for easier updates between 
*    requests and allows for the expected configuration to be update if any previous changes were
*    deemed okay.
*/
function createMonitoredCookie(value, count, cert, settings, res){
    const expected = {cert: cert, count: count, name: "Sess-Token", init: settings};
    var cipher = crypto.createCipheriv('aes-256-cbc', secretKey, IV);
    var encrypted = cipher.update(JSON.stringify(expected), "utf8", "base64");
    encrypted += cipher.final("base64");

    settings = convertSettings(settings);
    settings.monitored = {level: "high", message: encrypted};
    res.cookie("Sess-Token", value, settings);
    res.cookie("test-one", "hello", {secure: true, sameSite: "none", monitored: {level:"highc", message:"test one"}});
    //res.cookie("test-two", "again", {sameSite: "none", monitored: {level:"high", message: ""}, secure: true});
    //res.cookie("test-three", "I_hope", {secure: true, sameSite: "none", monitored: {level:"lowc", message:""}});
    //res.cookie("test-four", "you_are_well", {sameSite: "none", monitored: {level:"low", message: "test two"}, secure: true});
}


/**
*  This function checks whether the monitored session token is valid and either invalidates the token and redirects the 
*    user to the landing page or updates the token and redirects the user to the home page depending on the results.
*    there are a few exceptions to this for functionality and performance.
*/
function checkExistingSession(req, res, next){
    // First we check if the user even has a token
    console.log(req.url);
    var token = req.cookies["Sess-Token"];
    if (token === undefined){  
        // If they don't and are trying to go to the landing page, make an account, or login we allow the request to continue 
        //   essentially if they are going through the proper channels to login its fine
        if((req.url == "/") || (req.url == "/registration") || (req.url == "/login")){
            next();
        }else{  // Otherwise, we redirect the user back to the landing page  
            res.redirect("/");
        }
    }else{
        // If they do have a token, but are trying to logout we simply pass the request on as the token 
        //   will be invalidated regardless
        if(req.url == "/logout"){
            next()
        }else{
            /**
            * Outside of the above cases, we first check if the session exists/is valid as theyre is no
            *   point peforming the later checks if it was never valid in the first place. In our case, 
            *   validity is determined by whether the session-id exists in our sessions database.
            */
            //var start = performance.now();
            connectDB();
            database.connect((err) => {
                if(err){
                    console.log("Error connecting to the database: " + err.stack);
                    res.status(500).send("Internal Server Error"); 
                }else{
                    database.query("SELECT user_id FROM sessions WHERE session_id=?", [token], function(err, results, fields){
                        if(err){
                            console.log("Error selecting from sessions: " + err.stack);
                            disconnectDB(database);
                            res.status(500).send("Internal Server Error");  
                        }else if(results.length != 1){
                            // If the results are 0 we know this isn't a valid token and invalidate the cookie
                            //   Also there should only be 1 session per token so multiple results also result in invalidation
                            console.log("ERROR: Multiple sessions found");
                            invalidateCookie(token, res);
                        }else{
                
                            // If the token is valid we then need to grab the browsers report
                            var monitors = req.headers["report"];
                            if (monitors == undefined){
                                console.log("ERROR: No report header");
                                invalidateCookie(token, res);
                            }else{
                            	monitors = monitors.split(";");
                            	signature = monitors.at(-1).split("=")[1];
                            	time = monitors.at(-2).split("=")[1];
                            	var monitor = -1;
                            	for(var i = 0; i < monitors.length; i++){  // As its a generic feature there may be mulitple monitored-cookie report pairs
                                    if(monitors[i].includes("Sess-Token")){
                                        monitor = decodeURIComponent(monitors[i].split("=")[1]);
                                    	break;
                                    }
                            	}
                            	// If no report exists, we know something is wrong and the cookie is immediatly invalidated
                            	if (monitor == -1){
                                    console.log("ERROR: No report found");
                                    invalidateCookie(token, res);
                            	}else{
                                    console.log("DEBUGGING monitor: " + monitor);
                                    readableReport = JSON.parse(monitor);
                            
                                    // Otherwise the server first decrypts the expected information it saved on the user's browser
                                    var decipher = crypto.createDecipheriv("aes-256-cbc", secretKey, IV);
                                    try{
                                        var decrypted = decipher.update(readableReport["M"], "base64", "utf8");
                                        decrypted += decipher.final("utf8");
                                    }catch(error){
                                        console.log("ERROR: unable to decrypt expected - " + error);
                                        invalidateCookie(token, res);
                                        return;
                                    }
                                    console.log("DEBUGGING decrypted: " + decrypted);
                                    decrypted = JSON.parse(decrypted);
                            
                                    var temp = monitors[0];
                                    monitors.slice(1,-1).forEach((monitor) => temp += ";" + monitor);
                                    // and grabs the browser's public key it saved for this cookie
                                    var browser_hmac = crypto.createHmac("sha256", Buffer.from(decrypted["cert"], 'hex'), "hex");
                                    browser_hmac.update(temp);
                                    var calculated_hmac = browser_hmac.digest("hex");
                                    //console.log(monitors.at(-1));
                                    //console.log(calculated_hmac);
                                    // Using this key, the server verifies the signature of the report to prove the report hasn't been tampared with
                                    if(!(calculated_hmac == monitors.at(-1).split("=")[1])){
                                        console.log("ERROR: invalid signature - " + temp);
                                        invalidateCookie(token, res);
                                    }else{
                                        // If unaltered, we check that the report is fresh. We do this
                                        //   by checking that the report's generated timestamp is within a 
                                        //   small window of the current time
                                        var time_diff = new Date() - Date.parse(time);
                                        //console.log(decrypted["name"]);
                                        //console.log(token);
                                        //console.log(decrypted["init"]);
                                        if(decrypted["name"] != "Sess-Token" || token != decrypted["init"]["V"]) {
                                            console.log("ERROR: Name and/or Value dont match espected");
                                            invalidateCookie(token, res);
                                        
                                        }else if(time_diff > 300000){  // Used 5 minutes because that felt reasonable
                                            console.log("ERROR: replayed response");
                                            invalidateCookie(token, res);
                                        
                                        // Then if fresh, we check that the expected and actual counts match    
                                        //}else if (readableReport["count"] != decrypted["count"]){
                                        //    console.log("ERROR: count doesnt match");
                                        //    invalidateCookie(token, res);
                                    
                                        // If they do and thus the cookie hasn't been stolen, we check if it was tampared with
                                        }else if(!validateChangelog(readableReport["CL"])){
                                            console.log("ERROR: changelog not empty");
                                            invalidateCookie(token, res);
                                        
                                        // We also check that the current and expected settings match to ensure the logging wasn't bypassed
                                        //   or cleared by evicting the cookie
                                        }else if(!validateCurrent(readableReport["CS"], decrypted["init"])){
                                            console.log("ERROR: settings changed without being logged");
                                            invalidateCookie(token, res);
                                        }else{
                                            //var stop = performance.now();
                                            //console.log("TESTING TIMERS: " + (stop-start));
                                            // If everything passes the cookie is valid, the expected information is updated, and the user is let in
                                            createMonitoredCookie(token, decrypted["count"]+1, decrypted["cert"], decrypted["init"], res);
                                            if(req.url == "/home"){
                                                req.uid = results[0].user_id;
                                                next();
                                            }else{
                                                res.redirect("/home");
                                            }
                                        }
                                    }
                                }
                            }
                        }                  
                    });
                } 
            });
        }
    }     
}
     
     
// Ensures that the session token validation is called first on any request to the server
app.all("*", checkExistingSession);


/**
*  The logic for the logout page. When logging out we delete the user's session token from the database and 
*      invalidate the copy stored by the server
*/
app.get("/logout", (req, res) => {
    const token = req.cookies["Sess-Token"];
    
    connectDB();
    database.connect(function(err){
        if(err){
            /**
            *  If we cannot connect to the database, we cannot remove the session from the records. However the next 
            *    time the user visits the site the counts should be off resulting in the cookie being invalidated anyway
            */
            console.error("Error connecting to the database: " + err.stack);
            res.status(500).send("Internal Server Error")
        }else{
            // Try to delete the session from the database 
            database.query("DELETE FROM sessions WHERE session_id=?", [token], function(err){
                if(err){
                    /**
                    *  Similar to the prior error case, if we are unable to remove the session from the 
                    *    database we cannot properly log the user out. For this reason we don't invalidate 
                    *    the browser's copy as similar to the previous error, the next time the server
                    *    sees the cookie it will be invalid anyway.
                    */
                    console.error("Error deleting from the sessions table: " + err.stack); 
                    disconnectDB(database);
                    res.status(500).send("Internal Server Error");
                }else{
                    // Once the session is deleted, invalidate the cookie and redirect to the landing page
                    disconnectDB(database);
                    res.cookie("Sess-Token", token, {maxAge: -1000000000000});
                    res.redirect("/");
                }
            });
        }
    });
});


/**
*  All requests to the website's landing page simply returns index.html
*/
app.all("/", (req, res) => {
    res.sendFile(__directory + "index.html");
});

/**
*  The logic for creating a new account for the website. Takes the provide information, namely 
*      the user's name, username, and password and creates a new entry in the users table of the database. 
*/
app.post("/registration", (req, res) => {
    var firstName = req.body.firstName;
    var lastName = req.body.lastName;
    var username = req.body.usernameReg;
    var password = req.body.passwordReg;
    
    // Sanity check incase the user tries to post directly rather than using the form on index.html
    if(firstName !== undefined && lastName !== undefined && username !== undefined && password !== undefined){
        connectDB();
        database.connect(function(err){
            if (err) {
                console.error("Error connecting to the database: " + err.stack);
                res.send("Error - Problem connecting to the database"); // Return strings rather than a 500 error to display error on the landing page
            }else{
                database.query(" SELECT user_id FROM users WHERE username=?", [username], function(err, results, fields){
                    if(err){
                        console.error("Error selecting from the users table: " + err.stack);
                        disconnectDB(database);
                        res.send("Error - Problem interacting with the database");
                    }else if(results.length != 0){  // Ensure the username hasn't already been taken
                        disconnectDB(database);
                        res.send("Error - Username unavailable");
                    }else{
                        database.query("INSERT INTO users (username, password, firstname, lastname) VALUES (?, ?, ?, ?)", [username, password, firstName, lastName], function(err, results, fields){
                            if(err){
                                console.error("Error inserting into users: " + err.stack);
                                disconnectDB(database);
                                res.send("Error - A problem occured during account creation");
                            }else{
                                database.end(function(err){
                                    if(err){
                                        console.error("Error closing connection to the database: " + err.stack);
                                        res.send("Error - Problem interacting with the database");
                                    }else if(username === "secret"){  // Just having a bit of fun
                                        res.send("Secret - Account Created");
                                    }else{
                                        res.send("Success - Account Created");
                                    }
                                });
                            }
                        });
                    }
                });
            }
        });
    }else{
        res.send("Error - Missing required fields");
    }
});


/**
*  The logic for authenticating the user. Ensures that the provide username and password match an account
*      in the users database table. If the user successfully logs in, we create a new session token for 
*      subsequent visits.
*/
app.post("/login", (req, res) => {
    var username = req.body.username;
    var password = req.body.password;
    
    // Grab the Cookie Manager's Certificate from the request
    console.log(req.headers["cookey"]);
    var browser_cert = req.headers["cookey"];
    
    var temp = "";
    for(var i=0; i < browser_cert.length; i++){
        if(browser_cert[i] == "%"){
            temp += browser_cert[i+1];
            temp += browser_cert[i+2];
            i = i + 2;
        }else{
            temp += browser_cert.charCodeAt(i).toString(16);
        }
    }
    console.log(temp)
    browser_cert=temp;
    
    
    // Another sanity check for users who dont use the provided form...a bit sus
    if(username !== undefined && password !== undefined){
        connectDB();
        database.connect(function(err){
            if(err){
                console.error("Error connecting to the database: " + err.stack);
                res.send("Error - Problem connecting to the database");
            }else{
                // Try to get the password and id associated with the provided username 
                database.query("SELECT password, user_id FROM users WHERE username=?", [username], function(err, results, fields){
                    if(err){
                        console.error("Error selecting from the users table: " + err.stack);
                        disconnectDB(database);
                        res.send("Error - Problem interacting with the database");
                    }else if(results.length != 1){
                        /**
                        *  If no results are returned then the username is not valid. Based on server behavior
                        *    it should be impossible for there to be more than 1 result returned.
                        */
                        disconnectDB(database);
                        res.send("Error - Invalid Credentials");
                    }else{
                        // Check the passwords match. Yes I was lazy and did plaintext rather than hashes
                        //   Listen this is about protecting cookies not passwords
                        var account = results[0];
                        if(!(password === account.password)){
                            disconnectDB(database);
                            res.send("Error - Invalid Credentials");
                        }else{
                            // If the passwords match, generate a new session token  
                            const sessionID = crypto.randomUUID();  // Create the token
                            
                            // Try to add the session to the database 
                            database.query("INSERT INTO sessions (session_id, user_id) VALUES (?, ?)", [sessionID, account.user_id], function(err, results, fields){
                                if(err){
                                    /** 
                                    *  If adding the session fails, the user is still properly authenticated but 
                                    *      they are not provided with a session token.
                                    */
                                    console.error("Error inserting into sthe sessions table: " + err.stack);
                                }else if(browser_cert === undefined){
                                    // Again its a successful login, but we can't track so its just a one time thing
                                    //   probably not good for how im implementing this server.
                                }else{
                                    // Generate sessionToken (authentication cookie) for the user's browser 
                                   createMonitoredCookie(sessionID, 2, browser_cert, {V: sessionID, S: 1, SS: 2, B: 1}, res);   
                                }
                                disconnectDB(database);
                                res.send("Success");
                            });
                        }
                    }
                });
            }
        });
    }else{
        res.send("Error - Missing required fields");
    }
});


/**
*  The logic for the user's homepage. 
*/
app.get("/home", (req, res) => {

    // user-id is passed through from the token validation to remove duplicate database queries
    var uid = req.uid;

    database.query("SELECT firstname, lastname, username FROM users WHERE user_id=?", uid, (err, results, fields) => {
        let homeCopy = homePage.slice();  // Create a copy of the homepage template
        if(err){
            // If a problem occurs, make the template renderable and send it without user cutomization
            disconnectDB(database);
            console.error("Error selecting from users: " + err.stack);
            homeCopy = homeCopy.replace("COLOR", "black");
            res.send(homeCopy);
        }else{
            // Replace the template placeholders with the user's name
            homeCopy = homeCopy.replace("FIRSTNAME", results[0].firstname);
            homeCopy = homeCopy.replace("LASTNAME", results[0].lastname);
            if(results[0].username === "dither"){
                /**
                *  Again just having fun. A little easter egg for a small group of
                *      friends who will likely never see this, but hey who knows.
                *      The world do be strange.
                */
                homeCopy = homeCopy.replace("COLOR", "#E10098"); // Rhodamine Red C
            }else{
                /**  To save my sanity, I had some fun and made the user's name appear in a
                *        random color
                */
                homeCopy = homeCopy.replace("COLOR", "#" + Math.floor(Math.random() * 16777215).toString(16));
            }
            disconnectDB(database);
            res.send(homeCopy);  // Regardless of the outcome, send the page
            
        }
    });
});

