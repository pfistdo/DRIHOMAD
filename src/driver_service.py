import json
import requests
import pandas as pd
import base64
from io import BytesIO
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class DriverService:
    def __init__(self):
        pass

    # get all drivers of a year
    def getDriversOfYear(self, year):
        url = f"http://ergast.com/api/f1/{year}/drivers.json"
        response = requests.get(url)
        allDrivers = json.loads(response.text)
        return allDrivers["MRData"]["DriverTable"]["Drivers"]

    # get all gps of a year
    def getRacesOfYear(self, year):
        url = f"https://ergast.com/api/f1/{year}.json"
        response = requests.get(url)
        allRaces = json.loads(response.text)
        return allRaces["MRData"]["RaceTable"]["Races"]

    # get a single placement of a driver of a specific race
    def getSinglePlacement(self, year, driver, round):
        url = f"https://ergast.com/api/f1/{year}/{round}/drivers/{driver}/results.json"
        response = requests.get(url)
        placement = json.loads(response.text)
        if not placement['MRData']['RaceTable']['Races']: # if driver did not drive race return 0
            return 0
        else:
            return placement['MRData']['RaceTable']['Races'][0]['Results'][0]['position']

    # get all placements of a year of a specific driver
    def getAllPlacements(self, year, driver):
        url = f"https://ergast.com/api/f1/{year}/drivers/{driver}/results.json"
        response = requests.get(url)
        placement = json.loads(response.text)
        return placement['MRData']['RaceTable']['Races']

    def getAllSeasons(self):
        url = f"https://ergast.com/api/f1/seasons.json?limit=100"
        response = requests.get(url)
        seasons = json.loads(response.text)
        return seasons['MRData']['SeasonTable']['Seasons']

    def createDriverGraph(self, placements, row):
        height = list(map(int,placements[row][1:]))
        bars = tuple(range(1,len(height)+1))
        y_pos = np.arange(len(bars))
        
        plt.figure()
        plt.bar(y_pos, height)
        plt.xticks(y_pos, bars)
        plt.yticks(range(1,21), range(1,21))
        plt.title(placements[row][0])
        plt.xlabel('Race')
        plt.ylabel('Placement') 

        buf = BytesIO()
        plt.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return data

    def createAllSeasonsGraph(self, df):
        allSeasonsAvg = df.ratio.sum() / len(df.index)
        plt.figure()
        plt.plot(df.year, df.ratio)
        plt.axhline(y = 0.5, color = 'r', linestyle = '-')
        plt.axhline(y = allSeasonsAvg, color = 'g', linestyle = '--')
        plt.title('Home advantage ratio for all seasons')
        plt.xlabel('Season')
        plt.ylabel('Ratio') 

        buf = BytesIO()
        plt.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return data