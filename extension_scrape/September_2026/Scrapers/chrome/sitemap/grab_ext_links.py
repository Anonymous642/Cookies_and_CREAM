import requests
from bs4 import BeautifulSoup as bs
"""
Uses the previously identified sitemap pages to extract extension 
  URLs from the map 
"""

def parse_initial_urls(filename):
    """
    Loads the sitemap pages to check from the provided file
    args:
        filename (str) - The name of the file to load
    returns:
        A list of sitemap URLs to check
    """
    base_urls = []
    with open(filename) as fp:
        for line in fp.readlines():
            base_urls.append(line.strip())
    return base_urls
    
    
def main():
    """
    The main method. Loads the sitemap subpages, fetches them, and extracts
      extension URLs from each page
    """
    bases = parse_initial_urls("all_chrome_bases.txt")
    
    i = 0
    extension_urls = []
    for base in bases:
    
        raw_data = requests.get(base)
        processed_data = bs(raw_data.text, "html.parser")
        urls = processed_data.find_all("loc")
        for url in urls:
            extension_urls.append(url.get_text())
        
        # Debugish message to show script is still running (more for firefox than chrome)
        if i%100 == 0:
            print(f"{i}: {base}")
        i += 1
        

    print(f"Finished: {len(extension_urls)}")
    with open("all_ext_urls.txt", "w") as ofp:
        for url in extension_urls:
            ofp.write(f"{url}\n")
main()
    
    
