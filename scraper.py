import requests
from bs4 import BeautifulSoup
import csv

class NGOScraper:
  def __init__(self):
    self.base_url = "https://ngobase.org/"
    self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '\
                   'AppleWebKit/537.36 (KHTML, like Gecko) '\
                    'Chrome/75.0.3770.80 Safari/537.36'}
    self.countries = None

  # get all available country and return a dictionary {country : abbrv}
  def get_countries(self) -> dict:
    response = requests.get(self.base_url, headers=self.header)
    soup = BeautifulSoup(response.text, "html.parser")

    results = soup.find(id="ngo_country")

    options = results.find_all("option")

    countries = {}

    for op in options:
      key = op.text.lower()

      if key:
        countries[key] = op["value"]

    self.countries = countries

  def get_country_ngo(self, country: str):
    country = country.lower()
    if country in self.countries:
      path = country.replace(" ", "-")
      url = self.base_url + "c/" + self.countries[country] + "/" + path + "-ngos-charities"
      print("Retrieving from: " + url)

      data = []
  
      while url: 
        page = requests.get(url, headers=self.header)
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
      self.save_data(data, path)

    else: 
      print("Error: invalid url")

  def save_data(self, data, path: str):
    print("Saving data")

    with open("data/" + path, "w", newline="") as csvfile:
      fieldnames = ['name', 'website']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      writer.writerows(data)


if __name__ == "__main__":
  scraper = NGOScraper()
  scraper.get_countries()
  print(len(scraper.countries))
  scraper.get_country_ngo("iceland")
