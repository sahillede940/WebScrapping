from bs4 import BeautifulSoup
import requests
import re


url = "https://shipware.com/blog/fedexs-2025-general-rate-increase-explained/"
 
request_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
req = requests.get(url, headers=request_headers)
print(req.status_code)

soup = BeautifulSoup(req.content, "html.parser")
obj = soup.find("section", class_="post-content")
obj = obj.find_all(["p", "h2"])

title = soup.find("h1", class_="post-title").text
title = re.sub(r"\s+", " ", title)
title = re.sub(r"[^a-zA-Z0-9]", "_", title)

with open(f"./outputs/{title}.txt", "w", encoding="utf-8") as f:
    for tag in obj:
        if tag.name == "h2":
            f.write(f"\n{tag.text}\n")
        else:
            f.write(f"{tag.text}\n")