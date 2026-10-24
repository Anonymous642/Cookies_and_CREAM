"""
This file filters out any repeat Firefox extension URLs
"""

all_firefox_errors = []
with open("unique_firefox_addon_urls_errors.txt") as fp:
    for line in fp.readlines():
        all_firefox_errors.append(line.strip())
        
unique_firefox_errors = []
cheating = set()
for url in all_firefox_errors:
    try:
        temp_url = url.split("/firefox")[1]
        temp_url = temp_url.strip()

        if not temp_url in cheating:
            cheating.add(temp_url)
            unique_firefox_errors.append(temp_url)
    except:
        unique_firefox_errors.append(url)
        
print(len(unique_firefox_errors))
with open("cleaned_firefox_errors.txt", "w") as ofp:
    for url in unique_firefox_errors:
        ofp.write(f"{url}\n")
        
        
all_android_errors = []
with open("unique_android_addon_urls_errors.txt") as fp:
    for line in fp.readlines():
        all_android_errors.append(line.strip())
        
unique_android_errors = []
cheating_a = set()
for url in all_android_errors:
    try:
        temp_url = url.split("/android")[1]
        temp_url = temp_url.strip()
        if not temp_url in cheating_a:
            cheating_a.add(temp_url)
            unique_android_errors.append(temp_url)
    except:
        unique_android_errors.append(url)
        
print(len(unique_android_errors))
with open("cleaned_android_errors.txt", "w") as ofp:
    for url in unique_android_errors:
        ofp.write(f"{url}\n")
