import os
import csv
import json
"""
A file that divides extensions into sublists based on their permissions
"""


def load_extension_db(filename):
    """
    Load the full set of extensions from the provided csv
    params:
        filename (str) - the csv of extensions to load
    returns:
        a dictionary mapping extension hashes to their corresponding name, user count, and url
    """
    extensions = {}
    first = 1
    
    with open(filename, "r") as ifp:
        csv_reader = csv.reader(ifp, delimiter=",")
        for row in csv_reader:
            if first:
                first = 0
                continue
            
            extensions[row[0]] = [row[0], row[1], row[2], row[3]]
    return extensions
        

def output_results(filename, extensions):
    """
    A function to output the supplied extension list to a file
    params:
        filename (str) - the name of the output file
        extensions (list(str, str, str, str)) - a list of extensions to output 
    """
    print(f"{filename}: {len(extensions)}")  # print the number of extensions in each list for easier number crunching
    
    with open(filename, "w") as ofp:
        ofp.write("Extension Hash, Name, User Count, URL\n")
        for extension in extensions:
            ofp.write(f"{extension[0]}, {extension[1]}, {extension[2]}, {extension[3]}\n")
    
        
def main():
    """
    The main function and the main sorting aspect. Parses each extension manifest and
      catrgorizes them based on their permissions
    """
    # versioning
    v2 = []
    v3 = []
    
    # host permissions
    all_urls = []
    https = []
    http = []
    
    # extension APIs
    cookies = []
    web_request = [[], []]
    web_request_blocking = [[], []]
    declarative_net_request = []
    
    # content scripts
    scripts = []
    scripts_all_urls = []
    scripts_https = []
    scripts_http = []
    
    
    # Load the main dictionary of extension
    all_extensions = load_extension_db("android_hashed_extensions.csv")
    files = os.listdir("andriod")
    for filename in files:  
        extension_hash = filename.split(".json")[0].strip()  # get the extension hash from the manifest filename
        with open(f"andriod/{filename}", "r") as ifp:
            try:
                manifest = json.load(ifp)  # Parse the manifest
            except Exception as e:
                print(f"Error loading json {filename}: {e}")
                exit(-1)
            
            
            # versioning
            version = manifest["manifest_version"]
            if version == 2:
                v2.append(all_extensions[extension_hash])
            elif version == 3:
                v3.append(all_extensions[extension_hash])
            else:  # Honestly not sure how this woulf happen
                print(f"Error: unknon version {version} - {filename}")
                exit(-1)
            
            
            # host permissions + extension APIs
            if version == 3:  # only V3 extensions have the host_permissions tag
                host_permissions = None  # Even then its an optional
                try:
                    host_permissions = manifest["host_permissions"]
                except:
                    pass
                
                # We only assign extensions to a single host category as they are a hierarchy (all_urls <- https <- http <- all others... technically)
                if host_permissions is not None:
                    if "<all_urls>" in host_permissions or "*://*/*" in host_permissions:
                        all_urls.append(all_extensions[extension_hash])
                    elif "https://*/*" in host_permissions:
                        if "http://*/*" in host_permissions:
                            all_urls.append(all_extensions[extension_hash])
                        else:
                            https.append(all_extensions[extension_hash])
                    elif "http://*/*" in host_permissions:
                        http.append(all_extensions[extension_hash])
            
            permissions = None  # Simialrly, as some permissions just require their own tag, the "permissions" entry may not always be there    
            try:
                permissions = manifest["permissions"]
            except:
                pass
            
            if permissions is not None:  # However the extensions we care about all have mandatory "premissions" entries
                if "cookies" in permissions:
                    cookies.append(all_extensions[extension_hash])
                
                if "webRequest" in permissions:
                    if version == 2:  # Really only for Firefox and provides better granularity of permissioning
                        web_request[0].append(all_extensions[extension_hash])
                    else:
                        web_request[1].append(all_extensions[extension_hash])
                    
                    if "webRequestBlocking" in permissions:
                        if version == 2:
                            web_request_blocking[0].append(all_extensions[extension_hash])
                        else:
                            web_request_blocking[1].append(all_extensions[extension_hash])
                
                # There are two main declarative keys
                if "declarativeNetRequest" in permissions or "declarativeNetRequestWithHostAccess" in permissions:
                    declarative_net_request.append(all_extensions[extension_hash])
                
                if version == 2:  # V2 extensions declare host permissions (if the declare anything) in the "permissions" tag
                    if "<all_urls>" in permissions or "*://*/*" in permissions:
                        all_urls.append(all_extensions[extension_hash])
                    elif "https://*/*" in permissions:
                        if "http://*/*" in permissions:
                            all_urls.append(all_extensions[extension_hash])
                        else:
                            https.append(all_extensions[extension_hash])
                    elif "http://*/*" in permissions:
                        http.append(all_extensions[extension_hash])
            
            # content scripts
            content_scripts = None  # Again, not all extensions have scripts
            try:
                content_scripts = manifest["content_scripts"]
            except:
                pass
              
            if content_scripts is not None:
                scripts.append(all_extensions[extension_hash])
            
                # content scripts define their own host permissions. As such, we check every scripts scope
                site_sentinels = [0,0,0]
                for script in content_scripts:
                    try:
                        sites = script["matches"]
                    except:
                        continue
                    
                    # if a script has access to all urls, the extension alreadt has access to all pages so we stop checking
                    if "<all_urls>" in sites or "*://*/*" in sites:
                        site_sentinels[0] = 1
                        break
                    elif "https://*/*" in sites:
                        if "http://*/*" in sites:
                            site_sentinels[0] = 1
                            break
                        else:  # other wise if it only has a single broad permission, we mark it and keep checking
                            site_sentinels[1] = 1
                    elif "http://*/*" in sites:
                        site_sentinels[2] = 1
                
                # This is because, scripts are weird. If one script can access all HTTPS sites while another can
                #   access all HTTP sites, those two scripts affectly provide <all_urls> coverage while no single 
                #   script has those permissions
                if site_sentinels[0] or (site_sentinels[1] and site_sentinels[2]):
                    scripts_all_urls.append(all_extensions[extension_hash])
                elif site_sentinels[1]:
                    scripts_https.append(all_extensions[extension_hash])
                elif site_sentinels[2]:
                    scripts_http.append(all_extensions[extension_hash])
                
    
    # Output the results
    output_files = ["v2", "v3", "all_urls", "https", "http", "cookies", "webRequest_v2", "webRequest_v3", "webRequestBlocking_v2", "webRequestBlocking_v3", "declarativeNetRequest", "content_scripts", "content_scripts_all_urls", "content_scripts_https", "content_scripts_http"]
    output_lists = [v2, v3, all_urls, https, http, cookies, web_request[0], web_request[1], web_request_blocking[0], web_request_blocking[1], declarative_net_request, scripts, scripts_all_urls, scripts_https, scripts_http]
    for i in range(len(output_files)):
        output_results(f"android_{output_files[i]}.txt", output_lists[i])



if __name__ == "__main__":
    main()
