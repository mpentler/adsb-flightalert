# adsb-flightalert 0.5 - example script
# parse a running dump1090-whatever install's aircraft.json for particular criteria in a key
# for example squawk = 7700, flight = blah, etc
import json

import adsbflightalert
import time
import smtplib
import socket


## Matches get logged into JSON files in the following format:
# {
#   "flight": "SKW4879 ",
#   "hex": "a65598",
#   "squawk": "7500",
#   "link": "https://adsb.oarc.uk/?icao=a65598",
#   "alert_detected": "2023-09-26T23:06:28",
#   "alert_last_seen": "2023-09-26T23:06:28",
#   "alert_detection_stopped": "",
#   "alert_status": "active",
#   "last_seen": "2023-09-26T23:07:12"
# }
#
# {
#  "flight": "SKW4879 ",
#  "hex": "a65598",
#  "squawk": "7500",
#  "link": "https://adsb.oarc.uk/?icao=a65598",
#  "alert_detected": "2023-09-26T23:06:28",
#  "alert_last_seen": "2023-09-26T23:10:50",
#  "alert_detection_stopped": "2023-09-26T23:10:56",
#  "alert_status": "inactive",
#  "last_seen": "2023-09-26T23:07:12"
# }


def logAlerts(alerted_aircraft):
  print('Incoming/current aircraft count to be logged/updated: ' + str(len(alerted_aircraft)))

  ## File paths.
  current_emergencies_file_path = "./emergencies.json"
  historical_emergencies_file_path = "./emergencies_history.json"

  ## Use consistent timestamp for all entries made during this run.
  detection_time = time.strftime("%Y-%m-%dT%H:%M:%S")

  ## Read in the current and historical emergencies files.
  with open(current_emergencies_file_path, 'r') as current_emergencies_file:
    current_emergencies_json = json.load(current_emergencies_file)
  with open(historical_emergencies_file_path, 'r') as historical_emergencies_file:
    historical_emergencies_json = json.load(historical_emergencies_file)

  ## Iterate through the list of incoming/current alerts.
  for value in alerted_aircraft:
    ## Check to see if there is already an entry for this hex code which is active.
    ## If found, update the last seen time to now.
    is_new = True
    for entry in current_emergencies_json:
      if (entry['hex'] == value['hex']) and (entry['alert_status'] == "active"):
        entry['alert_last_seen'] = detection_time
        is_new = False
        ## NB: Deliberately not breaking here in case there are multiple entries with the same hex (shouldn't be)

    ## If the hex isn't in the current list of matches, add it.
    if (is_new):
      new_entry = dict()
      new_entry['flight'] = value['flight']
      new_entry['hex'] = value['hex']
      new_entry['squawk'] = value['squawk']
      new_entry['link'] = "https://adsb.oarc.uk/?icao=" + value['hex']
      new_entry['alert_detected'] = detection_time
      new_entry['alert_last_seen'] = detection_time
      new_entry['alert_detection_stopped'] = ""
      new_entry['alert_status'] = "active"
      current_emergencies_json.append(new_entry)

  ## We have now processed all incoming/current alerts.
  ## Any remaining active alerts which were not in the current list need to be marked as inactive.
  active_entries = [entry for entry in current_emergencies_json if entry['alert_status'] == "active"]
  for entry in active_entries:
    matching_entries_by_hex = [value for value in alerted_aircraft if value['hex'] == entry['hex']]
    if (len(matching_entries_by_hex) == 0):
      ## No match found, so this alert is no longer active.
      entry['alert_status'] = "inactive"
      entry['alert_detection_stopped'] = detection_time

  ## Any inactive alerts within the current emergencies json need to be moved across to the historical file.
  newly_inactive_entries = [entry for entry in current_emergencies_json if entry['alert_status'] == "inactive"]
  for entry in newly_inactive_entries:
    historical_emergencies_json.append(entry)

  ## All inactive alerts have now been added to the historical file.
  ## Remove them from the list of current emergencies.
  current_emergencies_json = [entry for entry in current_emergencies_json if entry['alert_status'] != "inactive"]

  ## Write the files back out
  with open(current_emergencies_file_path, 'w') as current_emergencies_file:
    current_emergencies_file.write(json.dumps(current_emergencies_json))
  with open(historical_emergencies_file_path, 'w') as historical_emergencies_file:
    historical_emergencies_file.write(json.dumps(historical_emergencies_json))


def main():
  global alert
  global already_alerting

  start_time = time.time()

  while True:
    current_time = time.time()

    if current_time > start_time + check_delay:
      scan_result = adsbflightalert.parseJSONfile(aircraft_json_path, filters)
      logAlerts(scan_result)
      start_time = current_time

    time.sleep(1)


alert = False  # alert state
already_alerting = False  # have we triggered an alert already?
check_delay = 5  # how often to check in seconds

aircraft_json_path = "/run/dump1090-fa/"  # path to aircraft.json file
# aircraft_json_path = "./"  # path to aircraft.json file
filters = [
  ("squawk", "7500"),
  ("squawk", "7600"),
  ("squawk", "7700"),
  #  ("area", [(55.5, -4.0), (56.5, -3.3)]) # not used in example, but this is how you do an area check - a list of two tuplea
]

print("==========")
print("adsb-flightalert is listening every " + str(check_delay) + " seconds for the following filters:\n")
filter_count = 0
for filter in filters:
  filter_count += 1
  print("Filter:", filter_count, filter[0], filter[1], sep=' | ')
print("==========")

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("==========")
    print("adsb-flightalert is exiting...")
    print("==========")
    # perhaps you could cancel any alerts or output pins here to clean up before exit?
