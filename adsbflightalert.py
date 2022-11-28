# adsb-flightalert 0.2
# parse a running dump1090 install for a particular squawk, such as 7700
import json

def parseJSONfile(aircraft_json_path, squawk_to_alert):
  current_alert_count = 0
  current_plane_count = 0
  alerted_aircraft = {} # full dict of any aircraft matching the squawk - there may not always only be 1!

  with open(aircraft_json_path + 'aircraft.json', 'r') as datafile:
    live_data = json.load(datafile) # load running aircraft.json

    for tracked_aircraft in live_data['aircraft']:
      current_plane_count += 1

      if 'squawk' in tracked_aircraft:
        if squawk_to_alert in tracked_aircraft['squawk']:
          current_alert_count += 1
          if 'flight' not in tracked_aircraft: % # Fix blank callsigns
            tracked_aircraft['flight'] = "NONE"
          alerted_aircraft[current_alert_count] = tracked_aircraft # add aircraft to alerted dict

  if (current_alert_count > 0):
    alerted_aircraft[0] = current_alert_count # set alerted planes count in dict
    return alerted_aircraft
  else:
    return 0

def logAlerts(alert_list):
  num_of_alerts = alert_list[0] # get num of alerts

  while num_of_alerts > 0: # run through the dict
    tracked_aircraft = alert_list[num_of_alerts]
    print("Alert for: " + tracked_aircraft['squawk'] + " - Callsign: " + callsign)
    num_of_alerts -= 1 # loop

  print("Alerts sent:", alert_list[0])
