import os
import csv
"""
A simple file to determine missing manifests. The files comapares all the scraped manifests in the output directory
  against all hashes identified in previous steps. Serves as backup in case a process dies or a scrapers errors are 
  misreported (more likely to happen for chrome)
"""

def main():
    
    manifests = os.listdir("../manifests/Extensions/firefox")
    
    manifest_hashes = set()
    for manifest in manifests:
        manifest = manifest.split(".")[0].strip()
        manifest_hashes.add(manifest)
        
    
    with open("firefox_hashed_extensions.csv", "r") as ifp:
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
                missing_manifests.append((row_hash, url))
            
    with open("test.txt", "w") as ofp:
        for manifest in missing_manifests:
            ofp.write(f"{manifest[0]}, {manifest[1]}\n")
    
    
    
if __name__ == "__main__":
    main()
