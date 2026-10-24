"""
This file filters out any repeat Firefox extension URLs
"""

all_firefox_urls = []
with open("all_firefox_addon_urls.txt") as fp:
    for line in fp.readlines():
        all_firefox_urls.append(line.strip())
        
unique_firefox_urls = []
cheating = set()
broken_urls = []

for url in all_firefox_urls:
    try:
        temp_url = url.split("/firefox/addon/")[1]
        temp_url = temp_url.split("/")[0]
        temp_url = temp_url.strip()

        if not temp_url in cheating:
            cheating.add(temp_url)
            unique_firefox_urls.append(temp_url)
    except:
        broken_urls.append(url)
        
print(len(unique_firefox_urls))
with open("unique_firefox_addon_urls.txt", "w") as ofp:
    for url in unique_firefox_urls:
        ofp.write(f"{url}\n")
        
with open("unique_firefox_addon_urls_errors.txt", "w") as ofp:
    for url in broken_urls:
        ofp.write(f"{url}\n")
        
all_android_urls = []
with open("all_android_addon_urls.txt") as fp:
    for line in fp.readlines():
        all_android_urls.append(line.strip())
        
unique_android_urls = []
cheating_a = set()
broken_urls = []

for url in all_android_urls:
    try:
        temp_url = url.split("/android/addon/")[1]
        temp_url = temp_url.split("/")[0]
        temp_url = temp_url.strip()
        if not temp_url in cheating_a:
            cheating_a.add(temp_url)
            unique_android_urls.append(temp_url)
    except:
        broken_urls.append(url)
        
print(len(unique_android_urls))
with open("unique_android_addon_urls.txt", "w") as ofp:
    for url in unique_android_urls:
        ofp.write(f"{url}\n")
        
with open("unique_android_addon_urls_errors.txt", "w") as ofp:
    for url in broken_urls:
        ofp.write(f"{url}\n")
