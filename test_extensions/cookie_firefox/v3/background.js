browser.runtime.onMessage.addListener((req, sen, resp) => {
    console.log(req);
    // Filter between the 4 possible API endpoints
    if (req.func == "get"){
        if (req.name == "" || req.url == ""){  // Get call requires both values be set
            resp({status: -1, message: "Error: both name and url must be defined"});
        }else{
             // Build the search information
             var details = {name: req.name,
                            url: req.url}
             if (req.key != ""){
                 details.partitionKey = {topLevelSite: req.key};
             }
             if (req.store != ""){
                 details.storeId = req.store;
             }
             
             browser.cookies.get(details, (cookie) => {
                 if (cookie == null){ // Either something went wrong or the cookie doesnt exist
                     console.log("nonexistant cookie");
                     resp({status: -1, message: "No such cookie found"});
                 }else{
                     console.log("cookie found");
                     resp({status: 0, message: "cookie fetched", cookie: cookie}); // Cannot open the connection from the background script. Data must be sent from the popup.
                 }
             });
        }
    }else if (req.func == "getAll"){
        var details = {};  // Get all requires nothing be specified at all
        
        if (req.domain != ""){
            details.domain = req.domain;
        }
        
        if (req.name != ""){
            details.name = req.name;
        }
        
        if (req.key != ""){
            details.partitionKey = {topLevelSite: req.key};
        }
        
        if (req.path != ""){
            details.path = req.path;
        }
        
        if (req.secure){
            details.secure = true;
        }
        
        if (req.session){
            details.session = true;
        }
        
        if (req.store != ""){
            details.storeId = req.store;
        }
        
        if (req.url != ""){
            details.url = req.url;
        }
        
        console.log(details);
        browser.cookies.getAll(details, (cookies) => {
            console.log(cookies);
            resp({status: 0, message: "All matching cookies found", cookies: cookies});
        });
    }else if (req.func == "set"){
        if (req.url == ""){  // Set requires only a URL in order to know who the cookie belongs to
            resp({status: -1, message: "A URL must be defined"});
        }else{ 
            var details = {url: req.url};
        
            if (req.domain != ""){
                details.domain = req.domain;
            }
        
            if (!isNaN(req.expires)){
                details.expirationDate = req.expires;
            }
        
            if (req.http){
                details.httpOnly = true;
            }
        
            if (req.name != ""){
                details.name = req.name;
            }
        
            if (req.key != ""){
                details.partitionKey = {topLevelSite: req.key};
            }
        
            if (req.path != ""){
                details.path = req.path;
            }
        
            if (req.site != ""){
                details.sameSite = req.site;
            }
        
            if (req.secure){
                details.secure = true;
            }
        
            if (req.store != ""){
                details.storeId = req.store;
            }
        
            if (req.value != ""){
                details.value = req.value;
            }
        
            browser.cookies.set(details, (cookie) => {
                if (cookie == null){ // If null an error has occured
                    resp({status: -1, message: "Unable to set cookie", error: browser.runtime.lastError});
                }else{
                    resp({status: 0, message: "Cookie set", cookie: cookie});
                }
            });
        }
    }else if (req.func == "remove"){
        if (req.name == "" || req.url == ""){ // Behaves identically to get
            resp({status: -1, message: "Error: both name and url must be defined"});
        }else{
             var details = {name: req.name,
                            url: req.url}
             if (req.key != ""){
                 details.partitionKey = {topLevelSite: req.key};
             }
             if (req.store != ""){
                 details.storeId = req.store;
             }
             
             console.log(details);   
             browser.cookies.remove(details, (results) => {
                 if (results == null){
                     resp({status: -1, messge: "Unable to remove cookie", error: browser.runtime.lastError})
                 }else{
                     resp({status: 0, message: "cookie removed", details: results});
                 }
             });
        }
    }else{ // Sanity check that should be impossible
        resp({status: -1, message: "Error: Unknown command"});
    }
    return true;
});
