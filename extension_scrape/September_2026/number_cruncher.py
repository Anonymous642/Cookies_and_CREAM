"""
This file provides the main calculation engine for extension permissions
"""

def load_extensions(filename):
    """
    Loads extension hashes and user counts from the provided file
    params:
        filename (str) - The name of the file to load extensions from
    returns:
        a dictionary mapping extension hashes to their user counts 
    """
    extensions = {}
    user_count = 0
    with open(filename, "r") as ifp:
        sentinel = 1
        for line in ifp.readlines():
            if sentinel:
                sentinel = 0
                continue
                
            tokens = line.strip().split(",")
            temp = int(tokens[-2].strip())
            user_count += temp
            extensions[tokens[0].strip()] = temp
    
    print(f"{filename} - {user_count}")  # Also prints the total user count of all extensions in the file for ease        
    return extensions
    

def unique(extensions, print_messages):
    """
    This function iterates through supplied list of extension dicctionaries to determine the total unique extensions
      and user count across lists
    params:
        extensions (list(dict(str, int))) - a list of extension dictionaries to calculate the uniquw extensions across
        print_messages (list(str)) - a list of strings to use for output messages to keep output cleaner
    returns:
        None
    """
    extension_set = set()  # We use a set for easy inclusion tracking
    i = 0
    for database in extensions:
        user_count = extension_count = 0
        for key, value in database.items():
            if key not in extension_set:
                extension_count += 1 
                user_count += value
                extension_set.add(key)
        
        print(f"{print_messages[i]}: {extension_count} - {user_count}")
        i += 1


def intersection(database_one, database_two):
    """
    Calculates the intersection between two dictionaries
    params:
        database_one (dict(str, int)) - the dictionary being compared to database_two
        database_two (dict(str, int)) - the dictionary being crossrefernced 
    returns:
        a dictionary mapping extension hashes to user counts that represents the intersection of the two supplied dicts
    """
    intersect = {}
    extension_count = user_count = 0
    for key, value in database_one.items():
        if key in database_two.keys():
            extension_count += 1
            user_count += value
            intersect[key] = value
    
    print(f"{extension_count} - {user_count}")  # output total extension and user count of intersection dict (why make a second counting function when it could be built in) 
    return intersect
    
      
def main():
    """
    The main function and number cruncher
    """
    extension_class = "chrome"  # used to tell the system which file paths to load from (android, chrome, and firefox) 
    permission_files = ["v2", "v3", "all_urls", "https", "http", "cookies", "webRequest_v2", "webRequest_v3", "webRequestBlocking_v2", "webRequestBlocking_v3", "declarativeNetRequest", "content_scripts", "content_scripts_all_urls", "content_scripts_https", "content_scripts_http"]
    extension_databases = []
    
    # Load each permission file and get total user counts
    for filename in permission_files:
        extension_databases.append(load_extensions(f"permissions/{extension_class}/{extension_class}_{filename}.txt"))
    
    # Check total unique extensions across the three APIs and scripts as well as their user user counts
    print()
    unique([extension_databases[5],extension_databases[6],extension_databases[7], extension_databases[10], extension_databases[11]], [permission_files[5], permission_files[6], permission_files[7], permission_files[10], permission_files[11]])
    
    # Filter all API lists by those with <all_urls> permsissions
    print()
    all_urls = []
    for database in [extension_databases[5],extension_databases[6],extension_databases[7], extension_databases[10]]:
        all_urls.append(intersection(database, extension_databases[2]))
    all_urls.append(intersection(extension_databases[11], extension_databases[12]))  # Also filter the content scripts results, but based on the scripts_all_urls list
    
    # Check the total unique all_url extensions and user counts
    print()
    unique(all_urls, [permission_files[5], permission_files[6], permission_files[7], permission_files[10], permission_files[11]])
    
    # Check how many extensions have both webRequest and declarativeNetRequest permissions
    print()
    intersection(extension_databases[10], extension_databases[6])
    intersection(extension_databases[10], extension_databases[7])
    
    
        
        

if __name__ == "__main__":
    main() 
