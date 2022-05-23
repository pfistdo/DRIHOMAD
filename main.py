import requests
import json

season = "2021"
url = "http://ergast.com/api/f1/" + season + "/drivers.json"

payload = {}
headers = {}

# response = requests.request("GET", url, headers=headers, data=payload)
response = requests.get(url)
allDrivers = json.loads(response.text)

for driver in allDrivers["MRData"]["DriverTable"]["Drivers"]:
    print(driver["givenName"])