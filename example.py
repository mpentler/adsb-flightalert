# adsb-flightalert 0.6 - example script
# parse a running dump1090/readsb install's aircraft.json for particular criteria in a key
# for example squawk = 7700, flight = blah, etc

import json
import time
import adsbflightalert

current_emergencies_file_path = "./emergencies.json"
historical_emergencies_file_path = "./emergencies_history.json"

aircraft_json_path = "/run/readsb/aircraft.json"

check_delay = 5  # seconds

filters = [
    ("squawk", "7500"),
    ("squawk", "7600"),
    ("squawk", "7700"),
]


# JSON functions
def load_json_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_json_file(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_aircraft_data(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {"aircraft": []}


# Process the alerts
def get_reason(squawk):
    if squawk == "7500":
        return "Hijack"
    elif squawk == "7600":
        return "Radio failure"
    elif squawk == "7700":
        return "General Emergency"
    return "Unknown"


# Pop alerts into the log files
def logAlerts(matches, full_snapshot):
    detection_time = time.strftime("%Y-%m-%dT%H:%M:%S")

    current_emergencies = load_json_file(current_emergencies_file_path)
    historical_emergencies = load_json_file(historical_emergencies_file_path)

    seen_hexes = {
        aircraft.get("hex")
        for aircraft in full_snapshot.get("aircraft", [])
        if aircraft.get("hex")
    }

    for result in matches:
        aircraft = result["aircraft"]

        hex_code = aircraft.get("hex")
        if not hex_code:
            continue

        # Check if already active
        existing = None
        for entry in current_emergencies:
            if entry["hex"] == hex_code and entry["alert_status"] == "active":
                existing = entry
                break

        if existing:
            existing["alert_last_seen"] = detection_time
            continue

        # New alert
        squawk = aircraft.get("squawk")
        reason = get_reason(squawk)

        new_entry = {
            "flight": aircraft.get("flight", "").strip(),
            "hex": hex_code,
            "squawk": squawk or "",
            "link": "https://your.tar1090.instance/tar1090/?icao=" + hex_code,
            "alert_detected": detection_time,
            "alert_last_seen": detection_time,
            "alert_detection_stopped": "",
            "alert_status": "active"
        }

        current_emergencies.append(new_entry)

        # This is where you would put some kind of notification code, such as sending an email
        # or lighting an LED, or whatever you want!

    # Check if any alerts are inactive
    for entry in current_emergencies:
        if entry["alert_status"] == "active":
            if entry["hex"] not in seen_hexes:
                entry["alert_status"] = "inactive"
                entry["alert_detection_stopped"] = detection_time

    # Put inactive alerts in history
    still_active = []
    for entry in current_emergencies:
        if entry["alert_status"] == "inactive":
            historical_emergencies.append(entry)
        else:
            still_active.append(entry)

    save_json_file(current_emergencies_file_path, still_active)
    save_json_file(historical_emergencies_file_path, historical_emergencies)


# Main loop
def main():
    start_time = time.time()

    while True:
        current_time = time.time()

        if current_time > start_time + check_delay:
            data = load_aircraft_data(aircraft_json_path)
            matches = adsbflightalert.filter_aircraft(data, filters)

            logAlerts(matches, data)

            start_time = current_time
        time.sleep(1)


# Initial load
print("==========")
print(f"Emergency logger is listening every {check_delay} seconds for:")
for i, f in enumerate(filters, start=1):
    print("Filter:", i, f[0], f[1], sep=" | ")
print("==========")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("==========")
        print("Emergency logger is exiting...")
        print("==========")
