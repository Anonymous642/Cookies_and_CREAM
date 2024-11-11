var response = false;
var request = false;

var target = "";

function setUpEventHandlers(){
    document.addEventListener("DOMContentLoaded", (event) => {
        document.getElementById("permissionButton").addEventListener("click", (event) => {
            browser.permissions.request({origins: ["<all_urls>"]});
            document.getElementById("targetDiv").style.display="inline"; 
            document.getElementById("rulesDiv").style.display="inline"; 
            document.getElementById("saveConf").style.display="inline"; 
            document.getElementById("outputDiv").style.display="inline"; 
            document.getElementById("permissionButton").remove();
        });
        document.getElementById("request").addEventListener("click", (event) => {request = document.getElementById("request").checked ? true : false;});
        document.getElementById("response").addEventListener("click", (event) => {response = document.getElementById("response").checked ? true : false;});
        document.getElementById("saveConf").addEventListener("click", (event) => {
            document.getElementById("status").value = "";
            target = document.getElementById("targetSite").value;
            
            if (target == ""){
                document.getElementById("status").style.color = "red";
                document.getElementById("status").innerText = "A target must be defined";
            }else{
                if (request){
                    browser.runtime.sendMessage({func: "request", target: target});
                    document.getElementById("status").style.color = "green";
                    document.getElementById("status").innerText = "Rule Added";
                }
                if (response){
                    browser.runtime.sendMessage({func: "response", target: target});
                    document.getElementById("status").style.color = "green";
                    document.getElementById("status").innerText = "Rule Added";
                }        
            
            }  
        });
    });
}

setUpEventHandlers();
