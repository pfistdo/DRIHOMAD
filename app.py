from flask import Flask, render_template, request
import pandas as pd

from src.driver_service import DriverService

app = Flask(__name__)
app.config.from_object('config_flask')  # load config

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
    races = ds.getRacesOfYear(year)

    # load demonyms to convert nationality to country
    placementsFrame = pd.read_csv('static/resources/demonyms.csv')
    df = pd.DataFrame(placementsFrame)
    df = df.drop_duplicates()

    # dataframe for average and home placements
    driverPlacementAvgs = pd.DataFrame(
        columns=['Driver', 'Average placement', 'Home placement'])

    # variables to save placements of drivers
    driverPlacementsCols = ['Driver']
    for i in range(len(races)):
        driverPlacementsCols.append(str(i+1))
    driverPlacements = []

    for driver in drivers:
        hadHomeRace = False
        placements = []      # placements of current driver
        homePlacements = []  # placements at home GP of current driver
        allPlacements = ds.getAllPlacements(year, driver['driverId'])  # unparsed results from REST API
        if len(allPlacements) == len(races):  # if driver completed all races
            for race in allPlacements:
                # add placement to list of placements
                placements.append(race['Results'][0]['position'])
                # check if race was home GP for current driver
                if race['Circuit']['Location']['country'] == df.loc[df['Origin'] == driver['nationality'], 'Region'].item():
                    # add placement to list of home placements
                    homePlacements.append(race['Results'][0]['position'])
                    hadHomeRace = True

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

            # save placements in array
            placements.insert(0, driver['familyName']) #add driver name to placements
            driverPlacements.append(list(placements))
    
    # create DF with all placements
    placementsFrame = pd.DataFrame(driverPlacements, columns=driverPlacementsCols)
    placementsFrame.columns = driverPlacementsCols
    #return render_template(template_name_or_list='pages/driversResult.html', result=driverPlacementAvgs, placements=placementsFrame)
    graphs = []
    for i in range(len(placementsFrame)):
        graphs.append(ds.createGraph(placementsFrame, i))
    print(f"{'Data 0: '}{graphs[0]}")
    print("=============================")
    print(f"{'Data 1: '}{graphs[1]}")

    return render_template(template_name_or_list='pages/driversResult.html', result=driverPlacementAvgs, placements=placementsFrame, graphs=graphs)


if __name__ == "__main__":
    app.run()