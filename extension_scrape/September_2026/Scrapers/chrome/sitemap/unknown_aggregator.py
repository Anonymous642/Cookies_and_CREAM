def main():
    
    full_list = []
    count = 0
    for i in range(10):
        with open(f"scrape_unknown_{i}.txt") as ifp:
            for line in ifp.readlines():
                full_list.append(line.strip())
                count += 1

    with open("to_check.txt", "w") as ofp:
        for url in full_list:
            ofp.write(f"{url}\n")
    
    print(count)
    
if __name__ == "__main__":
    main()
