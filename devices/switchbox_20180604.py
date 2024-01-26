"""SwitchboxD simulator

Version:
API docs: https://technical.blebox.eu/openapi_switchbox/openAPI_switchBox_20180604.html
"""
import time

from flask import Flask, request
from werkzeug.exceptions import BadRequest

from .kit import require_field, device_id

API_VERSION = "20180604"
START_TIME = time.time()

app = Flask(__name__)

STATE_AP_NETWORK = {
    "apEnable": True,
    "apSSID": "switchBoxD-g650e32d2217",
    "apPasswd": "my_secret_password"
}

STATE_NETWORK = {
    "ssid": "WiFi_Name",
    "pwd": "my_secret_password",
    "station_status": 5
}

STATE_RELAYS = {
    "0": 0,
}


@app.route("/", methods=["GET"])
def index():
    return f"I'm a switchBox (v{API_VERSION})"


@app.route("/api/device/state", methods=["GET"])
def info():
    return {
        "device": {
            "deviceName": f"My switchBox (v{API_VERSION})",
            "type": "switchBox",
            "apiLevel": API_VERSION,
            "hv": "0.2",
            "fv": "0.247",
            "id": device_id(__name__),
            "ip": "192.168.1.11"
        }
    }


@app.route("/api/device/uptime", methods=["GET"])
def api_device_uptime():
    return {"upTimeS": time.time() - START_TIME}


@app.route("/api/ota/update", methods=["POST"])
def api_ota_update():
    return


@app.route("/api/device/network", methods=["GET"])
def api_device_network():
    res = {
        **STATE_AP_NETWORK,
        **STATE_NETWORK,
        "bssid": "70:4f:25:24:11:ae",
        "ip": "192.168.1.11",
        "mac": "bb:50:ec:2d:22:17",
        "tunnel_status": 5,
        "apEnable": True,
        "apSSID": "switchBox-g650e32d2217",
        "apPasswd": "my_secret_password",
        "channel": 7
    }
    res.pop("pwd")
    return res


@app.route("/api/device/set", methods=["POST"])
def api_device_set():
    STATE_AP_NETWORK.update({
        "apEnable": require_field(request.json, ".network.apEnable", bool),
        "apSSID": require_field(request.json, ".network.apSSID", str),
        "apPasswd": require_field(request.json, ".network.apPasswd", str),
    })

    return {
        "device": {
            "deviceName": f"My switchBox (v{API_VERSION})",
            "type": "switchBox",
            "apiLevel": API_VERSION,
            "hv": "0.2",
            "fv": "0.247",
            "id": device_id(__name__),
            "ip": "192.168.1.11"
        },
        "network": {
            "ssid": "WiFi_Name",
            "bssid": "70:4f:25:24:11:ae",
            "ip": "192.168.1.11",
            "mac": "bb:50:ec:2d:22:17",
            "station_status": 5,
            "tunnel_status": 5,
            "channel": 7,
            **STATE_AP_NETWORK,
        }
    }


@app.route("/api/wifi/scan", methods=["GET"])
def api_wifi_scan():
    return {
        "ap": [
            {
                "ssid": "Funny_WiFi_Name",
                "rssi": -60,
                "enc": 3
            },
            {
                "ssid": "Less_Funny_WiFi_Name",
                "rssi": -75,
                "enc": 4
            },
            {
                "ssid": "Not_Funny_WiFi_Name",
                "rssi": -90,
                "enc": 0
            }
        ]
    }


@app.route("/api/wifi/connect", methods=["POST"])
def api_wifi_connect():
    STATE_NETWORK.update({
        "ssid": require_field(request.json, ".ssid", str),
        "pwd": require_field(request.json, ".pwd", str),
    })
    return {
        "ssid": STATE_NETWORK["ssid"],
        "station_status": STATE_NETWORK["station_status"],
    }


@app.route("/api/wifi/disconnect", methods=["POST"])
def api_wifi_disconnect():
    STATE_NETWORK.update({
        "ssid": require_field(request.json, ".ssid", str),
        "pwd": require_field(request.json, ".pwd", str),
    })
    return {
        "ssid": STATE_NETWORK["ssid"],
        "station_status": STATE_NETWORK["station_status"],
    }


@app.route("/api/relay/state", methods=["GET"])
def api_relay_state():
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"]
            },
        ]
    }


@app.route("/api/relay/extended/state", methods=["GET"])
def api_relay_extended_state():
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"],
                "stateAfterRestart": 2,
                "defaultForTime": 0,
            },
        ],
    }


@app.route("/api/relay/set", methods=["POST"])
def api_relay_set():
    relays = require_field(request.json, ".relays")
    if not isinstance(relays, list):
        raise BadRequest("Bad payload: .relays must be a list")

    if not (len(relays) == 1):
        raise BadRequest("Error: this device has only one relay")

    # todo: forTime control
    states = {}
    for i, relay in enumerate(relays):
        lead = f".relays[{i}]"
        idx = str(require_field(relay, ".relay", int, _lead=lead))
        state = require_field(relay, ".state", int, _lead=lead)
        state = int(not STATE_RELAYS[idx]) if state == 2 else int(state)
        states[idx] = state

    if len(states) != len(relays):
        raise BadRequest("Error: duplicated relays")

    STATE_RELAYS.update(states)
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"]
            },
        ]
    }


@app.route("/s/<state>", methods=["GET"])
def s_state(state):
    relay = "0"
    STATE_RELAYS[relay] = int(not STATE_RELAYS[relay]) if state == 2 else int(state)
    return {
        "relays": [
            {
                "relay": 0,
                "state": STATE_RELAYS["0"]
            }
        ]
    }
