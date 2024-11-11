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
        document.getElementById("beforeSendSet").addEventListener("click", (event) => {beforeSet = document.getElementById("beforeSendSet").checked ? true : false;});
        document.getElementById("headersReceivedGet").addEventListener("click", (event) => {headersGet = document.getElementById("headersReceivedGet").checked ? true : false;});
        document.getElementById("headersReceivedSet").addEventListener("click", (event) => {headersSet = document.getElementById("headersReceivedSet").checked ? true : false;});
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
                if (beforeSet){
                    beforeName = document.getElementById("beforeSendSetName").value;
                    beforeValue = document.getElementById("beforeSendSetValue").value;
                    if (beforeName == "" || beforeValue == ""){
                        document.getElementById("status").style.color = "red";
                        document.getElementById("status").innerText = "BeforeSend: Both a name and value must be specified";
                    }else{
                        chrome.runtime.sendMessage({func: "beforeSet", target: target, name: beforeName, value: beforeValue});
                        document.getElementById("status").style.color = "green";
                        document.getElementById("status").innerText = "Rule Added";
                    }
                }
                if (headersGet){
                    chrome.runtime.sendMessage({func: "headersGet", target: target});
                    document.getElementById("status").style.color = "green";
                    document.getElementById("status").innerText = "Rule Added";
                }
                if (headersSet){
                    headersName = document.getElementById("headersReceivedSetName").value;
                    headersValue = document.getElementById("headersReceivedSetValue").value;
                    if (headersName == "" || headersValue == ""){
                        document.getElementById("status").style.color = "red";
                        document.getElementById("status").innerText = "HeadersReceived: Both a name and value must be specified";
                   }else{
                       chrome.runtime.sendMessage({func: "headersSet", target: target, name: headersName, value: headersValue});
                       document.getElementById("status").style.color = "green";
                       document.getElementById("status").innerText = "Rule Added";
                   }
               }
            }
            
            
            
        });
    });
}

setUpEventHandlers();
