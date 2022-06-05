from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np


from src.driver_service import DriverService

app = Flask(__name__)
app.config.from_object('config_flask')  # load config

drivers2 = ["VER", "LEC", "SAI"]  # test only


@app.route("/")
def home():
    return render_template("pages/index.html")


@app.route("/drivers")
def driver():
    return render_template("pages/drivers.html")


@app.route('/drivers/result', methods=['GET'])
def driversByYear() -> str:

    ds = DriverService()
    year = str(request.args.get('year'))

    # get drivers of year
    drivers = ds.getDriversOfYear(year)

    # get gps of year
    #races = ds.getRacesOfYear(year)

    # load demonyms to convert nationality to country
    data = pd.read_csv(r'resources/demonyms.csv')
    df = pd.DataFrame(data)
    df = df.drop_duplicates()

    # dataframe for average and home placements
    driverPlacementAvgs = pd.DataFrame(
        columns=['Driver', 'Average placement', 'Home placement'])

    # dataframe for all placements of drivers with home GP
    driverPlacements = pd.DataFrame(
        columns=['Driver', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22'])

    for driver in drivers:
        hadHomeRace = False
        placements = []      # placements of current driver
        homePlacements = []  # placements at home GP of current driver
        allPlacements = ds.getAllPlacements(year, driver.get(
            'driverId'))  # unparsed results from REST API
        if allPlacements:  # if driver drove a race this season
            for race in allPlacements:
                # add placement to list of placements
                placements.append(race['Results'][0]['position'])
                # check if race was home GP for current driver
                if race['Circuit']['Location']['country'] == df.loc[df['Origin'] == driver['nationality'], 'Region'].item():
                    # add placement to list of home placements
                    homePlacements.append(race['Results'][0]['position'])
                    hadHomeRace = True

            # unneeded? test only
            if len(placements) < 22:
                print(
                    f"{driver['familyName']}{' completed fewer races than expected!'}")
                # for i in range(len(placements)):
                #     print(f"{i}{': '}{placements[i]}")

        # calculate average placements for drivers with home GP
        if hadHomeRace:
            totalPlacements = 0
            totalHomePlacements = 0
            for placement in placements:
                totalPlacements += int(placement)
            averagePlacement = totalPlacements / len(placements)
            for placement in homePlacements:
                totalHomePlacements += int(placement)
            averageHomePlacement = totalHomePlacements / len(homePlacements)

            # add driver to data frame
            new_row = pd.DataFrame(
                {'Driver': driver['familyName'], 'Average placement': averagePlacement, 'Home placement': averageHomePlacement}, index=[0])
            driverPlacementAvgs = pd.concat(
                [new_row, driverPlacementAvgs.loc[:]]).reset_index(drop=True)

            # add placements to data frame
            new_row = pd.DataFrame({'Driver': driver['familyName'], '1': placements[0], '2': placements[1], '3': placements[2], '4': placements[3], '5': placements[4], '6': placements[5], '7': placements[6], '8': placements[7], '9': placements[8], '10': placements[9], '11': placements[10],
                                   '12': placements[11], '13': placements[12], '14': placements[13], '15': placements[14], '16': placements[15], '17': placements[16], '18': placements[17], '19': placements[18], '20': placements[19], '21': placements[20], '22': placements[21]}, index=[0])
            driverPlacements = pd.concat(
                [new_row, driverPlacements.loc[:]]).reset_index(drop=True)
    print(driverPlacementAvgs.to_string())
    print(driverPlacements.to_string())
    return render_template(template_name_or_list='pages/driversResult.html', result=driverPlacementAvgs, placements=driverPlacements)

@app.route('/plot')
def plot():

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

    print(data)

    return render_template('pages/plot.html', graph=data)

if __name__ == '__main__':
   app.run()

@app.route("/test")  # test only
def test():
    return render_template("test.html", title="Website title", drivers=drivers2)


if __name__ == "__main__":
    app.run()
