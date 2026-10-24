"""
This file parses all identified extension URLs to remove any duplicate URLs
  This file is a bit looser than the Firefox variant due to the Webstores
  URL structure
"""

all_urls = []
with open("all_ext_urls.txt") as fp:
    for line in fp.readlines():
        all_urls.append(line.strip())
        
unique_urls = []  # Output list (maintains order though not really necessary)
cheating = set()  # Set to make uniqueness checks easier 

for url in all_urls:
    url = url.split("?")[0]  # Remove any query parameters (e.g., language code)
    if not url in cheating:
        cheating.add(url)
        unique_urls.append(url)
        
# Report and save
print(len(unique_urls))
with open("unique_ext_urls", "w") as ofp:
    for url in unique_urls:
        ofp.write(f"{url}\n")
        

