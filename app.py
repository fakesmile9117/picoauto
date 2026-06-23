from flask import Flask, jsonify
import time

app = Flask(__name__)

relay_status = "off"
timer_end = 0

@app.route("/")
def home():
    return "Home Automation API"

@app.route("/home/on")
def relay_on():
    global relay_status, timer_end
    relay_status = "on"
    timer_end = 0
    return jsonify({"relay": relay_status, "timer_end": timer_end})

@app.route("/home/off")
def relay_off():
    global relay_status, timer_end
    relay_status = "off"
    timer_end = 0
    return jsonify({"relay": relay_status, "timer_end": timer_end})

@app.route("/home/timer/<int:h>/<int:m>/<int:s>")
def relay_timer(h, m, s):
    global relay_status, timer_end

    total_seconds = h * 3600 + m * 60 + s

    relay_status = "on"
    timer_end = int(time.time()) + total_seconds

    return jsonify({
        "relay": relay_status,
        "timer_end": timer_end
    })

@app.route("/home/status")
def status():
    global relay_status, timer_end

    if timer_end > 0 and int(time.time()) >= timer_end:
        relay_status = "off"
        timer_end = 0

    return jsonify({
        "relay": relay_status,
        "timer_end": timer_end
    })

if __name__ == "__main__":
    app.run()