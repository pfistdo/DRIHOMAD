import json
import requests
import pandas as pd
import base64
from io import BytesIO
import numpy as np
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

    def plot(self):
        df=pd.DataFrame({'x_values': range(1,11), 'y_values': np.random.randn(10) })

        left = [1, 2, 3, 4, 5]
        # heights of bars
        height = [10, 20, 36, 40, 5]
        # labels for bars
        tick_label = ['one', 'two', 'three', 'four', 'five']
        # plotting a bar chart
        plt.bar(left, height, tick_label=tick_label, width=0.8, color=['red', 'green'])

        # naming the y-axis
        plt.ylabel('y - axis')
        # naming the x-axis
        plt.xlabel('x - axis')
        # plot title
        plt.title('My bar chart!')

        buf = BytesIO()
        plt.savefig(buf, format="png")

        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        return data

    # return render_template('pages/plot.html', graph=data)