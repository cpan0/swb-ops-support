import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '\
'AppleWebKit/537.36 (KHTML, like Gecko) '\
           'Chrome/75.0.3770.80 Safari/537.36'}

base_url = "https://ngobase.org/"
url = "https://ngobase.org/c/GF/french-guina-ngos-charities"

while url: 
  print(f"Scraping {url}")

  page = requests.get(url, headers=headers)
  soup = BeautifulSoup(page.content, "html.parser")

  results = soup.find(id="main_content")

  # if not results:
  #   break

  postings = results.find_all("div", class_="ngo_listing_div")

  for p in postings:
  # Find NGO name
    name = p.find("h3", class_="ngo_name").find("a").text
    print(name)

    # Find NGO website link
    web_elm = p.find("img", alt="NGO website")
    if web_elm:
      link = web_elm.find_parent("a")
      if link and link.has_attr("href"):
        print("Website link:", link["href"])
    print()

  # Find next url
  next_url = None
  pagination = results.find("ul", class_="pagination")
  next_link = pagination.find("a", {"rel" : "next"})
  if next_link and link.has_attr("href"):
    next_url = next_link["href"]

  url = next_url
