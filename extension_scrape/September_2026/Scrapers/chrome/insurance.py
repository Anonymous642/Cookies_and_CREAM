import os
import csv
"""
A simple file that cross reference the manifests we already have with the
  main list of extension hashes to determine what still needs to be 
  scraped
"""


def main():
    
    manifests = os.listdir("../manifests/Extensions/unlabeled")
    debug_count = 0
    
    manifest_hashes = set()
    for manifest in manifests:
        manifest = manifest.split(".")[0].strip()
        manifest_hashes.add(manifest)
        
    
    with open("chrome_hashed_unlabeled.csv", "r") as ifp:
        missing_manifests = []
        sentinel = 1
        csv_reader = csv.reader(ifp, delimiter=",")
        for row in csv_reader:
            if sentinel:
                sentinel = 0
                continue
            
            row_hash = row[0]
            url = row[3]
            
            if row_hash not in manifest_hashes:
                debug_count += 1
                missing_manifests.append((row_hash, url))
    
    print(debug_count)
    with open("test.txt", "w") as ofp:
        for manifest in missing_manifests:
            ofp.write(f"{manifest[0]}, {manifest[1]}\n")
    
    
    
if __name__ == "__main__":
    main()
