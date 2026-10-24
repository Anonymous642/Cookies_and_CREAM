import csv

def parse_extensions_csv(filename):
    extensions = []
    first = True
    with open(filename) as fp:
        csv_reader = csv.reader(fp)
        for row in csv_reader:
            if first:
                first = False
                continue
            extensions.append(row)
    return extensions
    
    
def main():
    extensions = parse_extensions_csv("chrome_unlabled.csv")
    
    with open("chrome_unlabled_2.csv", "r") as ifp:
        csv_reader = csv.reader(ifp)
        for row in csv_reader:
            name = row[0]
            name = name.strip()[2:-1]
            
            url = row[-1]
            url = url.strip()[1:-2]
            
            count = row[1:-1]
            count = "".join(count)
            count = count.strip()[1:-1]
        
            extensions.append([name, count, url])

    with open("combined.csv", "w") as ofp:
        csv_writer = csv.writer(ofp)  
        csv_writer.writerow(["Name", "Users", "Link"])
        for ext in extensions:
            csv_writer.writerow(ext)


if __name__ == "__main__":
    main()
