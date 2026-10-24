from bs4 import BeautifulSoup
"""
A file to parse the Chrome Webstore's (https://chrome.google.com/webstore/sitemap) 
  sitemap and extract subpages to check
"""

# open the sitemap
with open("cws_sitemap_index.xml") as fp:
    sitemap = fp.read()
 
# parse the sitemap
xml = BeautifulSoup(sitemap, "lxml")

# identify URLs
locs = xml.find_all("loc")

cleaned = []
for loc in locs:
    cleaned.append(loc.get_text())
    
# save results (the filenames are the only Chrome specific aspect of this file)
with open("all_chrome_bases.txt", 'w') as ofp:
    for url in cleaned:
        ofp.write(f"{url}\n")
