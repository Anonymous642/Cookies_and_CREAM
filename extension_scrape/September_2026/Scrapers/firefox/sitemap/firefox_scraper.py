import csv
import math
import requests
import multiprocessing
from bs4 import BeautifulSoup as bs
"""
This file opens each identified URL and scrapes the extensions name, user count, and label.
  This also serves as a filter for bad URLs and extensions before the larger portions of the scrape
"""

STORE = "https://addons.mozilla.org/firefox/addon/"

def parse_names(filename):
    """
    Loads the names of Firefox extensions to scrape from the supplied file
    params:
        filename (str) - the name of the input file
    returns:
        a list of extensions to check
    """
    names = []
    with open(filename) as fp:
        for line in fp.readlines():
            line = line.strip()
            names.append(line)
    return names
    
    
def scrape(exts, num):
    """
    The main scraping functionality. This code uses the request library to open the extension page
      and parses the page with beautiful soup to extract the full name, user count, and label for the 
      extension. The function then filters the results into extensions, themes, 404s, and errors.
    params:
        exts (list(str)) - a list of extensions to check
        num (int) - the ID of the scraper
    """
    print(f"Process {num} started")
    errors = []
    missing = []
    themes = []
    extensions = []
    for name in exts:
        try:
            resp = requests.get(f"{STORE}{name}")
            
            # Track 404s for manual verification
            if resp.status_code == 404:
                missing.append(name)
                
            else:
                soupy_data = bs(resp.content, "html.parser")
             
                theme_header = soupy_data.find("div", "ThemeImage")
                
                # As themes have no JS/HTML we simply note them down and move on
                if not theme_header is None:
                    themes.append((name, f"{STORE}{name}"))
                else:
                    true_name = soupy_data.find("h1", "AddonTitle")
                    true_name = true_name.get_text("|").split("|")[0].strip()
 
                    metadata = soupy_data.find_all("span", "Badge-content")
                    count = 0
                    for meta in metadata:
                        temp = meta.get_text()
                        if "User" in temp:
                            token = temp.split("User")[0].strip()
                            if not token == "No":
                                count = token
                    
                    extensions.append((true_name, count, f"{STORE}{name}"))
        
        # Log other errors to rerun
        except Exception as e:
            errors.append(name)
    
    # Main output of extensions    
    with open(f"firefox_output_{num}.csv", "w") as ofp:
        writer = csv.writer(ofp)
        writer.writerow(["Name", "Users", "Link"])
        for ext in extensions:
            writer.writerow([ext[0], ext[1], ext[2]])
    
    # Identified themes for references
    with open(f"firefox_errors_{num}.txt", "w") as fp:
       for error in errors:
           fp.write(f"{error}\n")  
    
    # Pages that actually reported a 404 error
    with open(f"firefox_404s_{num}.txt", "w") as fp:
       for error in missing:
           fp.write(f"{error}\n") 
    
    # Pages were some other error occured
    with open(f"firefox_themes_{num}.txt", "w") as fp:
       for error in themes:
           fp.write(f"{error[0]}, {error[1]}\n") 
    
    print(f"Process {num} finished")
      
            
def main():
    """
    The main function. Reads in the main list of extensions to check, divides them among scraper processes, and starts the scrape
    """
    names = parse_names("to_check.txt")
    total_names = len(names)
    print(total_names)

    split = math.floor(total_names/10)
    processes = []
    
    for i in range(0,9):
        processes.append(multiprocessing.Process(target=scrape, args=(names[i*split : (i+1)*split], i)))
    processes.append(multiprocessing.Process(target=scrape, args=(names[9*split:], 9)))
    
    for process in processes:
        process.start()
    
    for process in processes:
        process.join()   
    
    
main()
