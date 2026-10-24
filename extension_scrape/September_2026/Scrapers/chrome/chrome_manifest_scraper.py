import csv
import json
import math
import time
import multiprocessing
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
"""
This file scrapes Chrome extension manifests using the selenium library and an
  online extension viewer 
"""


def parse_extensions_csv(filename):
    """
    Loads extensions to scrape from the supplied csv file
    params:
        filename (str) - the csv file containing extensions to scrape
    returns:
        a list of extension hash, url pairs to scrape 
    """
    extensions = []
    first = True
    with open(filename) as fp:
        csv_reader = csv.reader(fp)
        for row in csv_reader:
            if first:
                first = False
                continue
            
            ext_hash = row[0].strip()
            url = row[3].strip()
            extensions.append((ext_hash, url))
    return extensions


def parse_extensions_list(filename):
    """
    Loads extensions to scrape from the supplied text file. Used for all runs
      after the first because building a specific text file for this is easier
      than using a csv constantly
    """
    extensions = []
    with open(filename) as ifp:
        for line in ifp.readlines():
            line = line.strip().split(",")
            ext_hash = line[0].strip()
            url = line[1].strip()
            extensions.append((ext_hash, url))
    return extensions
           
           
def scraper(exts, num):
    """
    The main scraping functionality. The scraper opens a selenium, navigates to the extension viewer,
      and downloads the manifest. Specifically, it enters the extension URL, decompresses it, grab the
      manifest, and download it
    params:
        exts (lists(str)) - a list of extension hash, url pairs to scrape
        num (int) - the ID of the scrper
    returns:
        None
    """
    errors = []
    found_errors = []
    options = webdriver.FirefoxOptions()  # open the selenium window
    options.binary_location = "/snap/firefox/current/usr/lib/firefox/firefox"
    service = Service("/snap/bin/geckodriver")
    sel_con = webdriver.Firefox(service=service, options=options)
    sel_con.get("https://robwu.nl/crxviewer/")
    loop_count = 0
    
    for ext in exts:
        try:
            # Enter the extension URL into the page and press enter
            found = False
            input_box = sel_con.find_element(By.NAME, "crx")
            input_box.clear()
            input_box.send_keys(ext[1])
    
            submits = sel_con.find_elements("tag name", "input")
            for submit in submits:
                if (submit.get_attribute("type") == "submit") and (submit.get_attribute("value") == "Open in this viewer"):
                    submit.click()
                    break
    
            # wait for the extension to be decompressed (starts with 2 seconds and raised to 10, 20, 60, and 120 in future runs)
            time.sleep(10)
            
            # Grab the manifest file
            files = sel_con.find_elements("tag name", "li")
            for ext_file in files:
                if (ext_file.get_attribute("data-filename") == "manifest.json"):
                    ext_file.click()
                    break

            # Wait for manifest to load (start with 2 senconds and increase to 4 for future runs)
            time.sleep(4)
            
            # Download the manifest
            raw_manifest = sel_con.find_elements("class name", "line-nums")
            temp = raw_manifest[0].text
            found = True
            manifest = json.loads(temp)
            
            with open(f"../manifests/Extensions/unlabeled/{ext[0]}.json", "w") as fp:
                json.dump(manifest, fp)
            
            # Reset the page
            open_button = sel_con.find_element(By.ID, "open-crxviewer")
            open_button.click()
            
            # Wait for home page to load (start with 2 seconds, increase to 4 for future runs)
            time.sleep(4)
        except WebDriverException as wde:
            try:
                sel_con.close()
            except:
                pass
            sel_con = webdriver.Firefox(service=service, options=options)
            sel_con.get("https://robwu.nl/crxviewer/")
            if found:  # If "found" we know the extension existed but something went wrong with the download
                found_errors.append((ext[0], ext[1]))
            else:  # Otherwise we dont know if it exists or not
                errors.append((ext[0], ext[1]))
        except Exception as e:
            try:
                sel_con.close()
            except:
                pass
            sel_con = webdriver.Firefox(service=service, options=options)
            sel_con.get("https://robwu.nl/crxviewer/")
            if found:  # Again, a crash at this point shows that this is a good exetnsion that we need to go back for
                found_errors.append((ext[0], ext[1]))
            else:  # Otherwise we cant be certain and we need to try again
                errors.append((ext[0], ext[1]))
        
        # Debug message to get a sense of how long is remaining
        loop_count += 1
        if loop_count %100 == 0:
            print(f"Process {num}: {loop_count} pulled, {len(exts) - loop_count} remaining")
    
    # Cleanup and output
    sel_con.close() 
    with open(f"ext_proc{num}_errors.txt", "w") as efp:
        for error in errors:
            efp.write(f"{error}\n")
    with open(f"ext_proc{num}_found_errors.txt", "w") as efp:
        for error in found_errors:
            efp.write(f"{error}\n")
    print(f"Process {num} finished")
      
                
    
def main():
    """
    The main function. Loads the extensions to scrape, divides them amongst processes, and then starts the scrapers
    """
    #master_list = parse_extensions_csv("chrome_hashed_unlabeled.csv")
    master_list = parse_extensions_list("chrome_unlabeled_errors.txt")
    total_ext = len(master_list)
    split = math.floor(total_ext/10)
    master_list = master_list[split:2*split]
    total_ext = len(master_list)
    split = math.floor(total_ext/10)
    processes = []
    print(total_ext)
    
    for i in range(9):
        processes.append(multiprocessing.Process(target=scraper, args=(master_list[i*split : (i+1)*split], i)))
    processes.append(multiprocessing.Process(target=scraper, args=(master_list[9*split:], 9)))
    
    for process in processes:
        process.start()
    
    for process in processes:
        process.join()   
    

if __name__ == "__main__":
    main()
