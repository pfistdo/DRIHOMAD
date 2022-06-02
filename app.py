from flask import Flask, render_template, request
import pandas as pd


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

    # dataframe for results drivers
    resultFrame = pd.DataFrame(
        columns=['Driver', 'Average placement', 'Home placement'])

    for driver in drivers:
        hadHomeRace = False
        placements = []      # placements of current driver
        homePlacements = []  # placements at home GP of current driver
        allPlacements = ds.getAllPlacements(year, driver.get('driverId')) # unparsed results from REST API
        if allPlacements: # if driver drove a race this season
            for race in allPlacements:
                placements.append(race['Results'][0]['position']) # add placement to list of placements
                # check if race was home GP for current driver
                if race['Circuit']['Location']['country'] == df.loc[df['Origin'] == driver['nationality'], 'Region'].item():
                    homePlacements.append(race['Results'][0]['position']) # add placement to list of home placements
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
            resultFrame = resultFrame.append(resultFrame.append(
                {'Driver': driver['familyName'], 'Average placement': averagePlacement, 'Home placement': averageHomePlacement}, ignore_index=True))
    resultFrame = resultFrame.drop_duplicates()
    print(resultFrame.to_string())
    return render_template(template_name_or_list='pages/driversResult.html', drivers=drivers)


@app.route("/test")  # test only
def test():
    return render_template("test.html", title="Website title", drivers=drivers2)


if __name__ == "__main__":
    app.run()