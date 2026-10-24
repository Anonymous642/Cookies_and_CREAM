from bs4 import BeautifulSoup
"""
This file extracts all the subpages from the addons.mozilla.org/sitemap.xml
"""

# open the sitemap
with open("sitemap_firefox.xml") as fp:
    sitemap = fp.read()
 
# parse the xml
xml = BeautifulSoup(sitemap, "lxml")

# all urls are saved in a <loc> tag
locs = xml.find_all("loc")

cleaned = []
for loc in locs:
    cleaned.append(loc.get_text())

# output links (this filename is the only firefox specific thing in this file)
with open("firefox_addons_bases.txt", 'w') as ofp:
    for url in cleaned:
        ofp.write(f"{url}\n")
