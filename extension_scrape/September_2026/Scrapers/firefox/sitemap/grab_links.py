import requests
from bs4 import BeautifulSoup as bs
"""
This file parses the previously identified sitemap pages to extract
  extension URLs from the page
"""

def parse_initial_urls(filename):
    """
    Opens the supplied file to parse the sitemap URLs to check
    args:
        filename (str) - The name of the file containing the URLs to check
    returns:
        A list of URLs to check
    """
    base_urls = []
    with open(filename) as fp:
        for line in fp.readlines():
            base_urls.append(line.strip())
    return base_urls
    
    
def main():
    """
    The main method. Loads the base URLs to check, visits each site, and grabs 
      the extension URLs on each page
    """
    bases = parse_initial_urls("firefox_addons_bases.txt")
    
    i = 0
    firefox_addon_urls = []
    android_addon_urls = []  # Interestingly firefox has separate pages for andriod
    for base in bases:
    
        raw_data = requests.get(base)
        processed_data = bs(raw_data.text, "html.parser")
        urls = processed_data.find_all("loc")

        if "android" in base:
            for url in urls:
                android_addon_urls.append(url.get_text())
        else:
            for url in urls:
                firefox_addon_urls.append(url.get_text())
        
        # Simple output to show the script isnt frozen
        if i%100 == 0:
            print(f"{i}: {base}")
        i += 1
        

    print(f"Finished: {len(firefox_addon_urls) + len(android_addon_urls)} total, {len(firefox_addon_urls)} firefox, {len(android_addon_urls)} andoird")
    with open("all_firefox_addon_urls.txt", "w") as ofp:
        for url in firefox_addon_urls:
            ofp.write(f"{url}\n")

    with open("all_android_addon_urls.txt", "w") as ofp:
        for url in android_addon_urls:
            ofp.write(f"{url}\n")
main()
    
    
