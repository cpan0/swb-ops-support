import os
import csv

def save_data(data, path: str):
  print("Saving data")

  os.makedirs("data", exist_ok=True)

  filename = os.path.join("data", path + ".csv")
  with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ['name', 'website']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

  print("Data saved")