import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '\
'AppleWebKit/537.36 (KHTML, like Gecko) '\
           'Chrome/75.0.3770.80 Safari/537.36'}

URL = "https://ngobase.org/c/GF/french-guina-ngos-charities"
page = requests.get(URL, headers=headers)

# print(page.text)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="main_content")

postings = results.find_all("div", class_="ngo_listing_div")

for p in postings:
  name = p.find("h3", class_="ngo_name").find("a").text
  print(name)
  web_icon = p.find("img", alt="NGO website")
  if web_icon:
    link = web_icon.find_parent("a")
    if link and link.has_attr("href"):
      print("Website link:", link["href"])
  print()