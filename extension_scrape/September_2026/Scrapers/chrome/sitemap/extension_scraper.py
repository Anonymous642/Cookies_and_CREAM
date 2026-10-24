import csv
import math
import time
import multiprocessing
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup as bs

CHROMESTORE = "chromewebstore.google.com"
"""
This file scrapes basic information about each extension from the chrome webstore

For each extesion we look for three things. First, we double check the name 
  since the name in the URL isnt always complete. Second, we check chrome's
  catogorization of the extensions (i.e., extension, theme, undefined). Finally,
  we grab the reported user count for each extension.  

Along with getting some info about each extension, this scrape also helps us 
  identify (after several attempts) broken/inaccessible links. As such, this 
  also helps us further filter bad extensions from our results

Unlike Firefox which can be done entirely using the requests library, Chrome 
  returns different results for certain extensions accessed without a GUI. 
  Due to this, this file uses selenium to actually open each link in a GUI and
  extract the page's HTML. Sadly this visual component does mean it is a bit 
  slower to run than its sister script
"""

def initialize_lists(filename):
    """
    load extension urls from the supplied file
    params:
        filename (str) - the name of the file 
    returns:
        a list of extenion urls to check
    """
    urls = []
    with open(filename) as fp: 
        for line in fp.readlines():
            urls.append(line.strip()) 

    return urls


def scraper(exts, num):
    """
    The main scraping functionality. Opens the extension url in selenium and 
      attempts to grab the extension's name, user count, and label.
    params:
        exts (list(str)) - a list of extension urls to check
        num (int) - the ID of the scraper
    returns:
        None
    """
    errors = []
    themes = [] 
    unknown = []
    extensions = []
    i=0
    options = webdriver.FirefoxOptions()  # Start the selenium window
    options.binary_location = "/snap/firefox/current/usr/lib/firefox/firefox"
    service = Service("/snap/bin/geckodriver")
    sel_conn = webdriver.Firefox(service=service, options=options)  
    sentinel = 1
    
    while(len(exts) > 0):
        ext_link = exts.pop()
        try:
            sel_conn.get(ext_link)
            
            if sentinel:
                buttons = sel_conn.find_elements("tag name", "button")
                for button in buttons:
                    if (button.get_attribute("textContent").lower() == "reject all"):
                        button.click()
                        break
                sentinel = 0
                time.sleep(0.5)
            
            # Check whether the url points to an extension or not
            soupy_data = bs(sel_conn.page_source, "html.parser")
            theme = soupy_data.find("a", "gqpEIe FjUAcd")
            if theme is None:  # Some extensions have no label, these are likely Chrome Apps and logged separately 
                unknown.append(ext_link)
            elif theme.get_text().lower() == "theme":  # We do not care about themese so we just note there existence and move on
                themes.append(ext_link)
            else:
                name_header = soupy_data.find("h1", "Pa2dE")
                name = name_header.get_text()
        
            
                user_headers = soupy_data.find("div", "F9iKBc")
                users = 0  
                for header in user_headers:
                    text = header.get_text("|").split(" ")[0].strip()
                    number = text.replace(",", "")
                    if number.isdigit(): 
                        users = text 
                
                extensions.append((name, users, ext_link))
        
            
        except WebDriverException as wde: 
            sel_conn = webdriver.Firefox(service=service, options=options)
            sentinel = 1 
            errors.append(ext_link)
        except:    
            errors.append(ext_link)
          
        # Debug output to give an idea of how far into the scrape we are  
        i += 1  
        if i%1000 == 0:
            print(f"\t{i} extensions checked, {len(exts)} remaining")  
        
    sel_conn.close()
    
    # Output all the results
    with open(f"scrape_output_{num}.csv", "w") as ofp:
        writer = csv.writer(ofp)
        writer.writerow(["Name", "Users", "Link"])
        for name, count, link in extensions:
            try:
                writer.writerow([name, count, link])
            except:
                pass

    if len(errors) > 0:
        with open(f"scrape_errors_{num}.txt", "w") as ofp:
            for issue in errors:
                ofp.write(f"{issue}\n")
                
    if len(themes) > 0:
        with open(f"scrape_themes_{num}.txt", "w") as ofp:
            for issue in themes:
                ofp.write(f"{issue}\n")
                
    if len(unknown) > 0:
        with open(f"scrape_unknown_{num}.txt", "w") as ofp:
            for issue in unknown:
                ofp.write(f"{issue}\n")



def main():
    """
    The main function. Loads all the urls to check, splits them across processes, and starts the scrape
    """
    print("Parsing Base Addresses: ", end ="")
    urls = initialize_lists("to_check.txt")
    print(f"COMPLETE\n\t{len(urls)} urls loaded\nBeginning To Scrape {CHROMESTORE}:")
 
    split = math.floor(len(urls)/10)
    processes = []
    for i in range(9):
        processes.append(multiprocessing.Process(target=scraper, args=(urls[i*split:(i+1)*split], i)))
    processes.append(multiprocessing.Process(target=scraper, args=(urls[9*split:], 9)))
    
    for process in processes:
        process.start()
        
    for process in processes:
        process.join() 
    
    


if __name__ == "__main__":
    main()
