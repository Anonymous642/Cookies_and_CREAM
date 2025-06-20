var id = 1;

chrome.runtime.onMessage.addListener((req, sen, resp) => {
    switch (req.func) {
        case "request":
            chrome.declarativeNetRequest.updateSessionRules({addRules: [{action: {type: "modifyHeaders", requestHeaders: [{header: "cookie", operation: "append", value: " test_cookie=im evil;"}]}, condition: {"urlFilter": req.target, resourceTypes: ["main_frame"]}, id: id}]});
            id ++;
            break;
        case "response":
            chrome.declarativeNetRequest.updateSessionRules({addRules: [{action: {type: "modifyHeaders", responseHeaders: [{header: "cookie", operation: "append", value: " test_cookie=im evil;"}]}, condition: {"urlFilter": req.target, resourceTypes: ["main_frame"]}, id: id}]})
            id ++;
            break;
    }
});

chrome.declarativeNetRequest.onRuleMatchedDebug.addListener((details) => {console.log(details)});
