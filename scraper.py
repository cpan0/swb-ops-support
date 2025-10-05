import requests
from bs4 import BeautifulSoup
import csv

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '\
'AppleWebKit/537.36 (KHTML, like Gecko) '\
           'Chrome/75.0.3770.80 Safari/537.36'}

base_url = "https://ngobase.org/"
url = "https://ngobase.org/c/GF/french-guina-ngos-charities"

data = []

while url: 
  print(f"Scraping {url}")

  page = requests.get(url, headers=headers)
  soup = BeautifulSoup(page.content, "html.parser")

  results = soup.find(id="main_content")

  if not results:
    break

  postings = results.find_all("div", class_="ngo_listing_div")

  for p in postings:
    # Find NGO name
    name = None
    name = p.find("h3", class_="ngo_name").find("a").text

    # Find NGO website link
    link = None
    web_elm = p.find("img", alt="NGO website")
    if web_elm:
      link_elm = web_elm.find_parent("a")
      if link_elm and link_elm.has_attr("href"):
        link = link_elm["href"]
    
    if name or link:
      data.append({"name": name, "website": link})

  # Find next url
  next_url = None
  pagination = results.find("ul", class_="pagination")
  next_link = pagination.find("a", {"rel" : "next"})
  if next_link and next_link.has_attr("href"):
    next_url = next_link["href"]

  url = next_url

print("Total NGOs collected:", len(data))

with open('data/ppp.csv', 'w', newline='') as csvfile:
    fieldnames = ['name', 'website']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
