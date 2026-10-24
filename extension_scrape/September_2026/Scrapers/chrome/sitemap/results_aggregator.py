import csv
"""
A simple file to concate the output from each scraper process into a single file
"""


def main():
    complete_list = []
    debug_count = 0
    duplicates = set()
    for i in range(10):
        try:
            with open(f"unknown_scrape_output_{i}.csv") as ifp:
                #for line in ifp.readlines():
                #    url = line.strip()
                #    if url not in duplicates:
                #        complete_list.append(line.strip())
                #        debug_count += 1
                #        duplicates.add(url)
                    
                reader = csv.reader(ifp)
                sentinel = 1
                for row in reader:
                    if sentinel:
                        sentinel = 0
                        continue
                    
                    if row[2] not in duplicates:
                        complete_list.append(row)
                        debug_count += 1
                        duplicates.add(row[2])
                        
        except FileNotFoundError as fnfe:
            continue
    
    with open("chrome_unlabled_2.csv", "w") as ofp:
        for theme in complete_list:
            ofp.write(f"{theme}\n")
        
        #writer = csv.writer(ofp)
        #writer.writerow(["Name", "Users", "Link"])
        #for row in complete_list:
        #    writer.writerow(row)
    
    print(debug_count)
                
if __name__ == "__main__":
    main()
