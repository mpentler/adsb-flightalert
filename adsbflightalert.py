# adsb-flightalert 0.5 - main library
# parse a running dump1090-whatever install's aircraft.json for particular criteria in a key
# for example squawk = 7700, flight = blah, etc
import json

def parseJSONfile(aircraft_json_path, filters):
  """
  Returns a dict of dicts of aircraft matching the filter, with a
  count of entries in dict[0], or returns 0 if there aren't any matching

  aircraft_json_path (str): full path to aircraft.json with
    trailing slash
  filters (list): filter tuples in form ("type", "text"),... etc
  """

  current_alert_count = 0
  inside_box_count = 0
  alerted_aircraft_list = {} # dict to store any aircraft matching the filter

  with open(aircraft_json_path + 'aircraft.json', 'r') as datafile:
    live_data = json.load(datafile) # load live aircraft.json file

    for tracked_aircraft in live_data['aircraft']:

      # fix any missing data in mode S returns
      if 'flight' not in tracked_aircraft: # Fix blank callsign
        tracked_aircraft['flight'] = "NONE"
      if 'squawk' not in tracked_aircraft: # Fix blank squawk
        tracked_aircraft['squawk'] = "XXXX"

      for filter in filters: # iterate through the filters for each plane in tbe json
        filter_type = filter[0]
        filter_text = filter[1]

        if filter_type != "area": # non-area filters
          if filter_type in tracked_aircraft:
            if filter_text in tracked_aircraft[filter_type]:
              current_alert_count += 1
              tracked_aircraft['matched'] = filter_type
              alerted_aircraft_list[current_alert_count] = tracked_aircraft # add aircraft to alerted dict
        else: # area filter
          if 'lat' in tracked_aircraft:
            if isInsideBox(filter_text, tracked_aircraft):
              inside_box_count += 1
              current_alert_count += 1
              tracked_aircraft['matched'] = filter_type
              alerted_aircraft_list[current_alert_count] = tracked_aircraft # add aircraft to inside-the-box dict

  # todo: add support for more than one area filter?
  if (inside_box_count > 0):
    print(inside_box_count, "aircraft in user-defined box")

  if (current_alert_count > 0):
    alerted_aircraft_list[0] = current_alert_count # set alerted planes count in dict. currently planes
    # are counted twice if they are caught by two filters in the same pass
    return alerted_aircraft_list
  else:
    return 0

def isInsideBox(coords_box, tracked_aircraft):
  """
  Checks to see if a passed aircraft's position is within the passed in
  coordinates.

  coords_box (list): contains two tuples containing (x, y) coords
  tracked_aircraft (dict): aircraft to check
  """
  plane_y = tracked_aircraft['lat']
  plane_x = tracked_aircraft['lon']
  y1 = coords_box[0][0]
  y2 = coords_box[1][0]
  x1 = coords_box[0][1]
  x2 = coords_box[1][1]

  b = (x1 < plane_x < x2) and (y1 < plane_y < y2)
  return b
