chrome.webRequest.onBeforeRequest.addListener((dets) => {
    console.log("onBeforeRequest");
    console.log(dets);
},
{urls: ["<all_urls>"]},
["requestBody", "extraHeaders"]);

chrome.webRequest.onBeforeSendHeaders.addListener((dets) => {
    console.log("onBeforeSendHeaders");
    console.log(dets);
},
{urls: ["<all_urls>"]},
["requestHeaders", "extraHeaders"]);

chrome.webRequest.onSendHeaders.addListener((dets) => {
    console.log("onSendHeaders");
    console.log(dets);
},
{urls: ["<all_urls>"]},
["requestHeaders", "extraHeaders"]);

chrome.webRequest.onCompleted.addListener((dets) => {
    console.log("onCompleted");
    console.log(dets);
},
{urls: ["<all_urls>"]},
["responseHeaders", "extraHeaders"]);

chrome.webRequest.onResponseStarted.addListener(function(details) {
    console.log("onResponseStarted");
    console.log(details);
}, 
{urls: ["<all_urls>"]},
["responseHeaders", "extraHeaders"]);

chrome.webRequest.onHeadersReceived.addListener(function(details) {
    console.log("onHeadersReceived");
    console.log(details);
},
{urls: ["<all_urls>"]},
["responseHeaders", "extraHeaders", "blocking"]);
