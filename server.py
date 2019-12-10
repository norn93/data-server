from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    with open("/home/pi/webserver/log.log", "r") as f:
        lines = f.readlines()
    n = len(lines)
    n = min(60*24*6, n)
    temperatures = []
    dates = []
    for line in lines[-n::6*10]:
        fields = line.split(",")
        dates.append(":".join(fields[0].strip().split(" ")[-1].split(".")[0].split(":")[0:2]))
        temperatures.append(float(fields[1].strip()))
    current_temperature = lines[-1].split(",")[-1]
    return render_template("temperature.html", temperature = current_temperature, data = temperatures, labels = dates)

@app.route("/settings")
def settings():
    with open("/home/pi/webserver/log.log", "r") as f:
        lines = f.readlines()
    current_temperature = lines[-1].split(",")[-1]
    with open("/home/pi/webserver/setpoint.txt", "r") as f:
        setpoint = f.read()
    return render_template("settings.html", temperature = current_temperature, setpoint = setpoint)

@app.route("/settings/<set_temperature>")
def setTemperature(set_temperature):
    with open("/home/pi/webserver/setpoint.txt", "w+") as f:
        f.write(set_temperature)
    return "<h1>Setting setpoint to " + set_temperature + "</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
