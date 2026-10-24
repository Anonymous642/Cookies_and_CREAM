import csv
import hashlib

def main():
    
    extension_database = {}
    index = 0
    
    with open("combined.csv") as ifp:
        sentinel = 1
        csv_reader = csv.reader(ifp, delimiter=",")
        for row in csv_reader:
            if sentinel:
                sentinel = 0
                continue
            
            #if len(row) > 5:
            #    print(f"Bad length: {index} - {row}")
            #    continue
            
            name = row[0].strip()
            count = row[1]
            url = row[2].strip()
            
            if name == "":
                print(f"Missing Name: {index} - {url} - {row}")
                
            if not isinstance(count, int):
                temp = count.replace(",", "")
                temp = temp.replace("+", "")
                temp = temp.strip()
                try:
                    count = int(temp)
                except ValueError:
                    print(f"Bad user count: {index} - {url} - {row}")
                    
                
            url_hash =  hashlib.sha256(url.encode()).hexdigest()
            if url_hash in extension_database.keys():
                print(f"Collision: {index} - {name}, {url} - {row}")
                print(extension_database[url_hash])
            else:
                extension_database[url_hash] = [name, count, url]
            index += 1
            
    with open("chrome_hashed_unlabeled.csv", "w") as ofp:
        csv_writer = csv.writer(ofp)
        csv_writer.writerow(["Url Hash", "Name", "Users", "URL"])
        for key, value in extension_database.items():
           csv_writer.writerow([key, value[0], value[1], value[2]])
            

if __name__ == "__main__":
    main()
    
            
