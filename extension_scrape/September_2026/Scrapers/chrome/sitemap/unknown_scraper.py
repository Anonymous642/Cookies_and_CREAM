import csv
import math
import time
import multiprocessing
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup as bs

CHROMESTORE = "chromewebstore.google.com"


def initialize_lists(filename):
    """

    """
    urls = []
    with open(filename) as fp: 
        for line in fp.readlines():
            urls.append(line.strip()) 

    return urls

def scraper(exts, num):
    themes = []
    errors = [] 
    unknown = []
    extensions = []
    bad_urls = []
    i=0
    options = webdriver.FirefoxOptions()
    options.binary_location = "/snap/firefox/current/usr/lib/firefox/firefox"
    service = Service("/snap/bin/geckodriver")
    sel_con = webdriver.Firefox(service=service, options=options)  
    sentinel = 1
    
    while(len(exts) > 0):
        ext_link = exts.pop()
        try:
            sel_con.get(ext_link)
            
            if sentinel:
                buttons = sel_con.find_elements("tag name", "button")
                for button in buttons:
                    if (button.get_attribute("textContent").lower() == "reject all"):
                        button.click()
                        break
                sentinel = 0
                time.sleep(0.5)
            
            
            loaded_page = sel_con.current_url
            url_end = loaded_page.split("/")[-1].strip()
            if url_end.lower() == "error":
                bad_urls.append(ext_link)
                i += 1
                continue
            
            soupy_data = bs(sel_con.page_source, "html.parser")
            theme = soupy_data.find("a", "gqpEIe FjUAcd")
            if theme is not None:
                if theme.get_text().lower() == "extension":
                    extensions.append(ext_link)
                elif theme.get_text().lower() == "theme":
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
                
                unknown.append((name, users, ext_link))
        
            
        except WebDriverException as wde: 
            sel_con = webdriver.Firefox(service=service, options=options)
            sentinel = 1 
            errors.append(ext_link)
        except Exception as e:
            #print(f"Process {num}: {ext_link} - {e}")
            errors.append(ext_link)
        
        i += 1  
        if i%1000 == 0:
            print(f"\t{i} extensions checked, {len(exts)} remaining")  
        
    sel_con.close()
    
    with open(f"unknown_scrape_output_{num}.csv", "w") as ofp:
        writer = csv.writer(ofp)
        writer.writerow(["Name", "Users", "Link"])
        for name, count, link in unknown:
            try:
                writer.writerow([name, count, link])
            except:
                pass

    if len(errors) > 0:
        with open(f"unknown_errors_{num}.txt", "w") as ofp:
            for url in errors:
                ofp.write(f"{url}\n")
                
    if len(themes) > 0:
        with open(f"unknown_scrape_themes_{num}.txt", "w") as ofp:
            for url in themes:
                ofp.write(f"{url}\n")
                
    if len(extensions) > 0:
        with open(f"unknown_scrape_extensions_{num}.txt", "w") as ofp:
            for url in extensions:
                ofp.write(f"{url}\n")
    
    if len(bad_urls) > 0:
        with open(f"unknown_scrape_404s_{num}.txt", "w") as ofp:
            for url in bad_urls:
                ofp.write(f"{url}\n")


def main():
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
