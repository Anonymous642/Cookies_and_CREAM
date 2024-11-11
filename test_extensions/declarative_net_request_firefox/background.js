var id = 1;

browser.runtime.onMessage.addListener((req, sen, resp) => {
    switch (req.func) {
        case "request":
            browser.declarativeNetRequest.updateSessionRules({addRules: [{action: {type: "modifyHeaders", requestHeaders: [{header: "cookie", operation: "append", value: " test_cookie=im in pain;"}]}, condition: {"urlFilter": req.target, resourceTypes: ["main_frame"]}, id: id}]});
            id ++;
            break;
        case "response":
            browser.declarativeNetRequest.updateSessionRules({addRules: [{action: {type: "modifyHeaders", responseHeaders: [{header: "cookie", operation: "append", value: " test_cookie=im in pain;"}]}, condition: {"urlFilter": req.target, resourceTypes: ["main_frame"]}, id: id}]})
            id ++;
            break;
    }
});

