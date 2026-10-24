var id = 1;

browser.runtime.onMessage.addListener((req, sen, resp) => {
    console.log(req)
    switch (req.func) {
        case "request":
            browser.declarativeNetRequest.updateSessionRules({addRules: [{action: {type: "modifyHeaders", requestHeaders: [{header: "cookie", operation: "append", value: " test_cookie=not suspicious;"}]}, condition: {"urlFilter": req.target, resourceTypes: ["main_frame"]}, id: id}]});
            id ++;
            break;
        case "response":
            browser.declarativeNetRequest.updateSessionRules({addRules: [{action: {type: "modifyHeaders", responseHeaders: [{header: "set-cookie", operation: "set", value: " test_cookie=lets make clear;"}]}, condition: {"urlFilter": req.target, resourceTypes: ["main_frame"]}, id: id}]})
            id ++;
            break;
    }
});

