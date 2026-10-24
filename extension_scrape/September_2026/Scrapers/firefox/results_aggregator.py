import csv
"""
A simple file to aggregate the output files of all the scraper processes into a single list
"""


def main():
    complete_list = []
    debug_count = 0
    duplicates = set()
    for i in range(10):
        with open(f"firefox_proc{i}_errors.txt") as ifp:
            for line in ifp.readlines():
                line = line.strip()
                tokens = line.split(",")
                ext_hash = tokens[0].strip()[2:-1]
                url = tokens[1].strip()[1:-2]
                complete_list.append((ext_hash, url))
                debug_count += 1
                
        #with open(f"firefox_themes_{i}.txt") as ifp:
        #    for line in ifp.readlines():
        #        tokens = line.split(",")
        #        url = tokens[1].strip()
        #        if url not in duplicates:
        #            complete_list.append(line.strip())
        #            debug_count += 1
        #            duplicates.add(url)
                    
            #reader = csv.reader(ifp)
            #sentinel = 1
            #for row in reader:
            #    if sentinel:
            #        sentinel = 0
            #        continue
                    
            #    if row[2] not in duplicates:
            #        complete_list.append(row)
            #        debug_count += 1
            #        duplicates.add(row[2])
    
    with open("firefox_errors.txt", "w") as ofp:
        for extension in complete_list:
            ofp.write(f"{extension[0]}, {extension[1]}\n")
        
        #for theme in complete_list:
        #    ofp.write(f"{theme}\n")
        
        #writer = csv.writer(ofp)
        #writer.writerow(["Name", "Users", "Link"])
        #for row in complete_list:
        #    writer.writerow(row)
    
    print(debug_count)
                
if __name__ == "__main__":
    main()
