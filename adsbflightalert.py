# adsb-flightalert 0.4 - main library
# parse a running dump1090-whatever install's aircraft.json for a particular item in a key
# for example squawk = 7700, flight = blah, etc
import json

def parseJSONfile(aircraft_json_path, filters):
  """
  Returns a dict of dicts of aircraft matching the filter, with a
  count in [0], or returns 0 if there aren't any matching

  aircraft_json_path (str): full path to aircraft.json with
    trailing slash
  filters (tuple): filter tuples in form ("type", "text")
  """

  current_alert_count = 0
  current_plane_count = 0
  alerted_aircraft_list = {} # dict to store any aircraft matching the filter

  with open(aircraft_json_path + 'aircraft.json', 'r') as datafile:
    live_data = json.load(datafile) # load live aircraft.json file

    for tracked_aircraft in live_data['aircraft']:
      current_plane_count += 1

      for filter in filters:
        filter_type = filter[0]
        filter_text = filter[1]

        if filter_type in tracked_aircraft:
          if filter_text in tracked_aircraft[filter_type]:
            current_alert_count += 1
            if 'flight' not in tracked_aircraft: # Fix blank callsigns
              tracked_aircraft['flight'] = "NONE"
            tracked_aircraft['matched'] = filter_type
            alerted_aircraft_list[current_alert_count] = tracked_aircraft # add aircraft to alerted dict
            logAlert(tracked_aircraft)

  if (current_alert_count > 0):
    alerted_aircraft_list[0] = current_alert_count # set alerted planes count in dict
    return alerted_aircraft_list
  else:
    return 0

def logAlert(alerted_aircraft): # send to stdout
  """
  Logs an alerted aircraft to stdout

  alerted_aircraft (dict): the alerted aircraft's record
  """
  # add time/date to log? if running as service there is no need
  # if not then it would be useful. can i detect which somehow?
  print(alerted_aircraft['matched'], "alert for - Hex:", alerted_aircraft['hex'], "Squawk:", alerted_aircraft['squawk'], "Callsign:", alerted_aircraft['flight'])
