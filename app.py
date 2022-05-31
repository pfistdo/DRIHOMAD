from flask import Flask, render_template, request
import json
import requests

app = Flask(__name__)
app.config.from_object('config_flask') #load config

drivers2 = ["VER", "LEC", "SAI"] #test only

@app.route("/")
def home():
    return render_template("pages/index.html")

@app.route("/drivers")
def driver():
    return render_template("pages/drivers.html")

@app.route('/drivers/result', methods=['GET'])
def driversByYear() -> str:
    app.logger.info(request.args.get('year'))
    year = str(request.args.get('year'))
    url = "http://ergast.com/api/f1/" + year + "/drivers.json"
    app.logger.info(url)
    response = requests.get(url)
    allDrivers = json.loads(response.text)
    drivers = allDrivers["MRData"]["DriverTable"]["Drivers"]
    return render_template(template_name_or_list='pages/driversResult.html', drivers=drivers)

@app.route("/test") #test only 
def test():
    return render_template("test.html", title="Website title", drivers=drivers2)

if __name__ == "__main__":
    app.run()