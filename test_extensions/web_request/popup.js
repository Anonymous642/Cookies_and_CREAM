var beforeGet = false;
var beforeSet = false;
var headersGet = false;
var headersSet = false;

var target = "";
var beforeName = "";
var beforeValue = "";
var beforeDest = "";
var headersName = "";
var headersValue = "";

function setUpEventHandlers(){
    document.addEventListener("DOMContentLoaded", (event) => {
        document.getElementById("beforeSendGet").addEventListener("click", (event) => {beforeGet = document.getElementById("beforeSendGet").checked ? true : false;});
        document.getElementById("headersReceivedGet").addEventListener("click", (event) => {headersGet = document.getElementById("headersReceivedGet").checked ? true : false;});
        document.getElementById("saveConf").addEventListener("click", (event) => {
            document.getElementById("status").value = "";
            target = document.getElementById("targetSite").value;
            
            if (target == ""){
                document.getElementById("status").style.color = "red";
                document.getElementById("status").innerText = "A target must be defined";
            }else{
                if (beforeGet){
                    chrome.runtime.sendMessage({func: "beforeGet", target: target});
                    document.getElementById("status").style.color = "green";
                    document.getElementById("status").innerText = "Rule Added";
                }
                if (headersGet){
                    chrome.runtime.sendMessage({func: "headersGet", target: target});
                    document.getElementById("status").style.color = "green";
                    document.getElementById("status").innerText = "Rule Added";
                }
            }        
        });
    });
}

setUpEventHandlers();
