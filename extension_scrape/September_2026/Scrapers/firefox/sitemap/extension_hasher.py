import csv
import hashlib

def main():
"""
The main function. Opens the supplied CSV of extensions, hashes the URL, and rebuilds the CSV
  for later manifest scraping steps. This files also serves as a way to check for broken CSV
  entries.
"""
    
    extension_database = {}
    index = 0
    
    # Opens the selected csv and reads rows. android_extensions.csv or firefox_extensions.csv in this directory
    with open("android_extensions.csv") as ifp:
        sentinel = 1
        csv_reader = csv.reader(ifp, delimiter=",")
        for row in csv_reader:
            if sentinel:
                sentinel = 0
                continue
            
            # Simplest check for malformated rows. Likely do to a ";" being misinterpreted as a delimiter
            if len(row) > 4:
                print(f"Bad length: {index} - {row}")
                continue
            
            name = row[0].strip()
            count = row[1]
            url = row[2].strip()
            
            # Check if the name is blank. Some pages actually have no name others may have broke for other reasons
            if name == "":
                print(f"Missing Name: {index} - {url} - {row}")
                
            # Cleans the user counts into an actual integer 
            if not isinstance(count, int):
                temp = count.replace(",", "")
                temp = temp.replace("+", "")
                temp = temp.strip()
                
                # If the count is not an int, its likely that the name was split into multiple columns causing text to be where the user count should be
                try:
                    count = int(temp)
                except ValueError:
                    print(f"Bad user count: {index} - {url} - {row}")
                    
            # The URLs are unique so we hash them to serve as a unique extension ID for later
            url_hash =  hashlib.sha256(url.encode()).hexdigest()
            # One final confirmation that there has been no issues with row formatting
            if url_hash in extension_database.keys():
                print(f"Collision: {index} - {name}, {url} - {row}")
                print(extension_database[url_hash])
            else:
                extension_database[url_hash] = [name, count, url]
            index += 1
    
    # Output the new hashes alongside each extension for future manifest scraping         
    with open("android_hashed_extensions.csv", "w") as ofp:
        csv_writer = csv.writer(ofp)
        csv_writer.writerow(["Url Hash", "Name", "Users", "URL"])
        for key, value in extension_database.items():
           csv_writer.writerow([key, value[0], value[1], value[2]])
            

if __name__ == "__main__":
    main()
    
            
