from flask import Flask, render_template
import os, sys
import subprocess
import json, datetime

HOME_DIR = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
LOG_FILENAME = "/home/pi/tap-switcher/log.log"
SETPOINT_FILENAME = "/home/pi/tap-switcher/setpoint.txt"
READINGS_PER_MINUTE = 1

if LOG_FILENAME == "<add this in>" or SETPOINT_FILENAME == "<add this in>":
    print("Please configure the paths!")
    exit(0)

app = Flask(__name__)

@app.route('/')
def index():
    with open(LOG_FILENAME, "r") as f:
        lines = f.readlines()
    n = len(lines)
    n = min(60*24*READINGS_PER_MINUTE, n)
    dates = []

    # Now, your custom field stuff
    temperatures = []
    humidities = []

    for line in lines[-n::READINGS_PER_MINUTE*10]:
        fields = line.split(",")
        dates.append(":".join(fields[0].strip().split(" ")[-1].split(".")[0].split(":")[0:2]))

        # Now, your custom field stuff
        temperatures.append(float(fields[1].strip()))
        humidities.append(float(fields[2].strip()))

    # Now, your custom field stuff
    current_temperature = lines[-1].split(",")[-2]
    current_humidity = lines[-1].split(",")[-1]

    return render_template("data.html",
        temperatures = temperatures, humidities = humidities, labels = dates)

@app.route("/settings")
def settings():
    with open(LOG_FILENAME, "r") as f:
        lines = f.readlines()

    # Now, your custom field stuff
    current_temperature = lines[-1].split(",")[-2]
    current_humidity = lines[-1].split(",")[-1]

    with open(SETPOINT_FILENAME, "r") as f:
        setpoint = f.read()
    return render_template("settings.html", temperature = current_temperature, humidity = current_humidity, setpoint = setpoint)

@app.route("/settings/<set_temperature>")
def setTemperature(set_temperature):
    with open(SETPOINT_FILENAME, "w+") as f:
        f.write(set_temperature)
    return "<h1>Setting setpoint to " + set_temperature + "</h1>"

@app.route("/recent")
def recent():
    result = "<h1>Recent</h1>"
    for line in subprocess.check_output(["tail", LOG_FILENAME]).decode("utf-8").split("\n"):
        result = result + "<p>" + line + "</p>"
    return result

@app.route("/status")
def status():
    date_str, temperature, humidity = subprocess.check_output(["tail", LOG_FILENAME]).decode("utf-8").split("\n")[-2].split(", ")
    this_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    healthy_dht = (datetime.datetime.now() - this_date).seconds < 70
    response = [
        {
            "name": "dht22",
            "healthy": healthy_dht,
            "detail" : {"lastDatetime": str(this_date)},
        },
        {
            "name": "temperature",
            "status:": temperature,
        },
        {
            "name": "humidity",
            "status": humidity,
        }
    ]
    return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
