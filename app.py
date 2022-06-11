from flask import Flask, g, render_template, request
from os.path import exists
import pandas as pd

from src.driver_service import DriverService

app = Flask(__name__)
app.config.from_object('config_flask')  # load config

@app.route("/")
def home():
    return render_template("pages/index.html")


@app.route("/singleSeason")
def driver():
    ds = DriverService()
    allSeasons = ds.getAllSeasons()
    return render_template("pages/selectSingleSeason.html", seasons=allSeasons)


@app.route('/singleSeason/result', methods=['GET'])
def calculateSingleSeason():
    ds = DriverService()
    year = str(request.args.get('year'))

    # get drivers of year
    drivers = ds.getDriversOfYear(year)

    # get gps(Grands Prix) of year
    races = ds.getRacesOfYear(year)

    # load demonyms to convert nationality to country
    demonyms = pd.read_csv('static/resources/demonyms.csv')
    demonyms = pd.DataFrame(demonyms)
    demonyms = demonyms.drop_duplicates()

    # dataframe(DF) for average and home placements
    driverPlacementAvgs = pd.DataFrame(
        columns=['DriverId', 'Driver', 'Average placement', 'Home placement'])

    # variables to save placements of drivers
    driverPlacementsCols = ['Driver']
    for i in range(len(races)):
        driverPlacementsCols.append(str(i+1))
    driverPlacements = []

    # mainloop
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
                if race['Circuit']['Location']['country'] == demonyms.loc[demonyms['Origin'] == driver['nationality'], 'Region'].item():
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

            # add driver to DF
            new_row = pd.DataFrame(
                {'DriverId': driver['driverId'], 'Driver': driver['familyName'], 'Average placement': averagePlacement, 'Home placement': averageHomePlacement}, index=[0])
            driverPlacementAvgs = pd.concat(
                [new_row, driverPlacementAvgs.loc[:]]).reset_index(drop=True)

            # save placements in array
            placements.insert(0, driver['familyName']) #add driver name to placements
            driverPlacements.append(list(placements))
       
    # calculate home advantage ratio
    totalHomeAdvantages = 0
    for index, row in driverPlacementAvgs.iterrows():
        if row['Average placement'] > row['Home placement']:
            totalHomeAdvantages+=1
    if len(driverPlacementAvgs) > 0:
        homeAdvantageRatio = totalHomeAdvantages / len(driverPlacementAvgs)
    else:
        homeAdvantageRatio = 0

    # create graph with placements for every driver
    graphs = []
    for i in range(len(driverPlacements)):
        graphs.append(ds.createDriverGraph(driverPlacements, i))
    graphs = graphs[::-1] # invert array to match driverPlacementAvgs position
    return render_template(template_name_or_list='pages/singleSeasonResult.html', result=driverPlacementAvgs, graphs=graphs, year=year, ratio=homeAdvantageRatio)

@app.route('/allSeasons', methods=['GET'])
def calculateAllSeasons():
    ds = DriverService()

    file = 'static/resources/allSeasons.csv'
    if not exists(file):
        with open(file, 'w') as f:
            f.write(f"{'year,ratio'}")
    allSeasons = pd.read_csv(file)
    allSeasons = pd.DataFrame(allSeasons)
    for season in ds.getAllSeasons():
        year = season['season']
        if int(year) not in allSeasons.values:
            print(f"{'Year '}{year}{' did not exist in csv'}")
        
            # get drivers of year
            drivers = ds.getDriversOfYear(year)

            # get gps(Grands Prix) of year
            races = ds.getRacesOfYear(year)

            # load demonyms to convert nationality to country
            demonyms = pd.read_csv('static/resources/demonyms.csv')
            demonyms = pd.DataFrame(demonyms)
            demonyms = demonyms.drop_duplicates()

            # dataframe(DF) for average and home placements
            driverPlacementAvgs = pd.DataFrame(
                columns=['DriverId', 'Driver', 'Average placement', 'Home placement'])

            # variables to save placements of drivers
            driverPlacementsCols = ['Driver']
            for i in range(len(races)):
                driverPlacementsCols.append(str(i+1))
            driverPlacements = []

            # mainloop
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
                        if race['Circuit']['Location']['country'] == demonyms.loc[demonyms['Origin'] == driver['nationality'], 'Region'].item():
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

                    # add driver to DF
                    new_row = pd.DataFrame(
                        {'DriverId': driver['driverId'], 'Driver': driver['familyName'], 'Average placement': averagePlacement, 'Home placement': averageHomePlacement}, index=[0])
                    driverPlacementAvgs = pd.concat(
                        [new_row, driverPlacementAvgs.loc[:]]).reset_index(drop=True)

                    # save placements in array
                    placements.insert(0, driver['familyName']) #add driver name to placements
                    driverPlacements.append(list(placements))

            # calculate home advantage ratio
            totalHomeAdvantages = 0
            # homeAdvantageRatio = 0
            for index, row in driverPlacementAvgs.iterrows():
                if row['Average placement'] > row['Home placement']:
                    totalHomeAdvantages+=1
            if len(driverPlacementAvgs) > 0:
                homeAdvantageRatio = totalHomeAdvantages / len(driverPlacementAvgs)
            else:
                homeAdvantageRatio = 0

            with open(file, 'a') as f:
                f.write("\n")
                f.write(f"{year}{','}{homeAdvantageRatio}")
            print('>> Added to csv')
    yearRatios = pd.read_csv(file)
    yearRatios = pd.DataFrame(yearRatios)
    yearRatios = yearRatios[yearRatios.ratio > 0] # remove ratios with 0
    # count seasons below 0.5, equal to 0.5 and above 0.5 advantage ratio
    seasonsUnder = yearRatios.apply(lambda x : True if x['ratio'] < 0.5 else False, axis = 1)
    seasonsEqual = yearRatios.apply(lambda x : True if x['ratio'] == 0.5 else False, axis = 1)
    seasonsAbove = yearRatios.apply(lambda x : True if x['ratio'] > 0.5 else False, axis = 1)
    seasonsUnder = len(seasonsUnder[seasonsUnder == True].index)
    seasonsEqual = len(seasonsEqual[seasonsEqual == True].index)
    seasonsAbove = len(seasonsAbove[seasonsAbove == True].index)

    # create graph for all seasons with ratio
    graph = ds.createAllSeasonsGraph(yearRatios)

    allSeasonsAvg = yearRatios.ratio.sum() / len(yearRatios.index)
    
    return render_template(template_name_or_list='pages/allSeasonsResult.html', graph=graph, under=seasonsUnder, equal=seasonsEqual, above=seasonsAbove, average=allSeasonsAvg)

if __name__ == "__main__":
    app.run()