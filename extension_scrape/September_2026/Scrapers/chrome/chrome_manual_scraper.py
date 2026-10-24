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
A single-process modified form of the manifest scraper to allow for a controlled 
  run through errors to double check nothing was missed 
"""


def parse_extensions_list(filename):
    """
    Loads the extensions to check from the supplied file
    params:
        filename (str) - the file with extensions to check
    returns:
        A list of extension hash, url pairs
    """
    extensions = []
    with open(filename) as ifp:
        for line in ifp.readlines():
            line = line.strip().split(",")
            ext_hash = line[0].strip()
            url = line[1].strip()
            extensions.append((ext_hash, url))
    return extensions      
                
    
def main():
    """
    The main function. Loads the extensions to check, loads them, and then waits for user input before continuing
    """
    master_list = parse_extensions_list("chrome_errors.txt")
    
    options = webdriver.FirefoxOptions()  # open the selenium window
    options.binary_location = "/snap/firefox/current/usr/lib/firefox/firefox"
    service = Service("/snap/bin/geckodriver")
    sel_con = webdriver.Firefox(service=service, options=options)
    sel_con.get("https://robwu.nl/crxviewer/")
    
    # start the scrap
    for i in range(len(master_list)):
        print(i)
        try:
            # enter the extension URL and press enter
            input_box = sel_con.find_element(By.NAME, "crx")
            input_box.clear()
            input_box.send_keys(master_list[i][1])
    
            submits = sel_con.find_elements("tag name", "input")
            for submit in submits:
                if (submit.get_attribute("type") == "submit") and (submit.get_attribute("value") == "Open in this viewer"):
                    submit.click()
                    break
            
            # Wait for the user before continuing. Allows us to download anything and reset the page
            input()
        except WebDriverException as wde:
            print(wde)
            try:
                sel_con.close()
            except:
                pass
            sel_con = webdriver.Firefox(service=service, options=options)
            sel_con.get("https://robwu.nl/crxviewer/")
            print(f"Crash {i}")
        except Exception as e:
            print(e)
            try:
                sel_con.close()
            except:
                pass
            sel_con = webdriver.Firefox(service=service, options=options)
            sel_con.get("https://robwu.nl/crxviewer/")
            print(f"Crash {i}")
    

if __name__ == "__main__":
    main()
