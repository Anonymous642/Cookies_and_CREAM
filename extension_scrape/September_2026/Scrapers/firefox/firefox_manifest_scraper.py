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
This file uses the selenium library to download the manifests of identified extensions.
  The extensions are spread across multiple processes to speed up the scrape. Errors 
  identified in early scrapes are rescraped with larger timeout windows to ensure valid
  extensions are not misreported.
"""


def parse_extensions_csv(filename):
    """
    Loads esxtensions to check from the supplied CSV file
    params:
        filename (str) - the name of a csv file contianing extensions to scrape
    returns:
        a list of extension hash, url pairs
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
    Loads extensions to check from the supplied text file. Used for every scrape after the first
      to make life easier
    params:
        filename (str) - the name of the text file containing extensions to scrape
    returns:
        a list of extension hash, url pairs
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
    The main scraping functionality. The function opens the extensions CRX in a selenium window, navigates
      to the manifest file, and downloads it. All manifests are saved to the output directory as the hash
      of the extension they belong to. The script then resets the window for the next extension.
    params:
        ext (list(str, str)) - a list of extension hash, url pairs to check
        num (int) - the ID of the processes
    returns:
        None
    """
    errors = []
    found_errors = []
    options = webdriver.FirefoxOptions()  # Create the initial selenium window
    options.binary_location = "/snap/firefox/current/usr/lib/firefox/firefox"
    service = Service("/snap/bin/geckodriver")
    sel_con = webdriver.Firefox(service=service, options=options) 
    sel_con.get("https://robwu.nl/crxviewer/")  # Online extension viewer/decompresser 
    loop_count = 0
    
    for ext in exts:
        try:
            # Enter the extension url on the page and press enter
            found = False
            input_box = sel_con.find_element(By.NAME, "crx")
            input_box.clear()
            input_box.send_keys(ext[1])
    
            submits = sel_con.find_elements("tag name", "input")
            for submit in submits:
                if (submit.get_attribute("type") == "submit") and (submit.get_attribute("value") == "Open in this viewer"):
                    submit.click()
                    break
    
            # Wait for page to load (initially 2 seconds, then test with 10, 20, 60 seconds)
            time.sleep(10)
            
            # Click in the manifest.json file
            files = sel_con.find_elements("tag name", "li")
            
            for ext_file in files:
                if (ext_file.get_attribute("data-filename") == "manifest.json"):
                    ext_file.click()
                    break

            # Wait for file to load (initially 2 seconds, then upped to 4 in all future experiments)
            time.sleep(4)
            
            # Download the manifest
            raw_manifest = sel_con.find_elements("class name", "line-nums")
            temp = raw_manifest[0].text
            found = True
            manifest = json.loads(temp)
            
            with open(f"../manifests/Extensions/firefox/{ext[0]}.json", "w") as fp:
                json.dump(manifest, fp)
            
            # Reset the page
            open_button = sel_con.find_element(By.ID, "open-crxviewer")
            open_button.click()
            
            # Wait for page to load (initially 2 seconds, then upped to 4 in all future experiments)
            time.sleep(4)
        except WebDriverException as wde:
            try:
                sel_con.close()
            except:
                pass
            sel_con = webdriver.Firefox(service=service, options=options) 
            sel_con.get("https://robwu.nl/crxviewer/")
            if found:  # If the error occured after the page loaded, meaning we know its a good extension
                found_errors.append((ext[0], ext[1]))
            else:  # page never loaded
                errors.append((ext[0], ext[1]))
        except Exception as e:
            try:
                sel_con.close()
            except:
                pass
            sel_con = webdriver.Firefox(service=service, options=options)
            sel_con.get("https://robwu.nl/crxviewer/")
            if found:  # Again, if the error occured after the page loaded, meaning we know its a good extension
                found_errors.append((ext[0], ext[1]))
            else:  # page stil never loaded
                errors.append((ext[0], ext[1]))
        
        # Some simple debug output to show the script is still running and give a sense of for how much longer
        loop_count += 1
        if loop_count %1000 == 0:
            print(f"Process {num}: {loop_count} - {len(exts) - loop_count} remaining")


    # Cleanup and output any errors for rescraping/verification
    sel_con.close() 
    with open(f"firefox_proc{num}_errors.txt", "w") as efp:
        for error in errors:
            efp.write(f"{error}\n")
    with open(f"firefox_proc{num}_found_errors.txt", "w") as efp:
        for error in found_errors:
            efp.write(f"{error}\n")
    print(f"Process {num} finished")
      
                
    
def main():
    """
    The main function. Loads the extensions to scrape, divides them across multiple processes, and starts the processes
    """
    #master_list = parse_extensions_csv("firefox_hashed_extensions.csv")
    master_list = parse_extensions_list("firefox_errors.txt")
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
