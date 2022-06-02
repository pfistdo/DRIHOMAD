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
    # app.logger.info(str(request.args.get('year')))

    ds = DriverService()
    year = str(request.args.get('year'))

    # get drivers of year
    drivers = ds.getDriversOfYear(year)

    # get gps of year
    races = ds.getRacesOfYear(year)

    # load demonyms to convert nationality to country
    data = pd.read_csv(r'resources/demonyms.csv')
    df = pd.DataFrame(data)
    df = df.drop_duplicates()

    result_cols = ["Driver", "Average placement", "Home placement"]
    resultFrame = pd.DataFrame(columns=result_cols)

    for driver in drivers:
        placements = []
        homePlacement = 0
        allPlacements = ds.getAllPlacements(year, driver.get('driverId'))
        print("========================================")
        #print(f"{driver.get('familyName')}{':'}{driver.get('driverId')}")
        #print(allPlacements)
        if allPlacements:
            for race in races:
                #placement = ds.getSinglePlacement(year, driver.get('driverId'), race.get('round'))
                #print(f"{'Placement: '}{allPlacements[int(race.get('round'))]['Results'][0]['position']}")
                if race['Circuit']['Location'].get('country') == df.loc[df['Origin'] == driver['nationality'], 'Region'].item():
                    #homePlacement = placement
                    homePlacement = ds.getSinglePlacement(year, driver.get('driverId'), race.get('round'))
                #placements.append(placement)
            # if len(placements) < 21:
            #     for placement in placements:
            #         print(f"{driver.get('familyName')}{' placed '}{placement}")
            placements = []
            #df.insert(driver.get('familyName'), "Age", [21, 23, 24, 21], True)
    return render_template(template_name_or_list='pages/driversResult.html', drivers=drivers)


@app.route("/test")  # test only
def test():
    return render_template("test.html", title="Website title", drivers=drivers2)


if __name__ == "__main__":
    app.run()
