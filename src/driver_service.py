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

    def createGraph(self, df, row):
        # heights of bars
        #height = df.iloc[row, 1:]

        placements = [5, 11, 9, 8, 5, 7, 10, 14, 7, 18, 6, 15, 5, 3, 10, 20, 14]
        races = tuple(range(len(placements)))
        y_pos = np.arange(len(races))

        # Create bars
        plt.bar(y_pos, placements)
        # plot title
        plt.title(df.iloc[row]['Driver'])

        buf = BytesIO()
        plt.savefig(buf, format="png")

        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        return data

    # return render_template('pages/plot.html', graph=data)