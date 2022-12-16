# adsb-flightalert 0.4 - example script
# search for emergency squawks and log them to stdout
import adsbflightalert
import time

alert = False # alert state
already_alerted = False # have we triggered current alert already?

check_delay = 60 # how often to check in seconds
filters = (("squawk","7700")) # tuple of tuples of filters, (type, text) - both strings in case of preceding 0s in the data
aircraft_json_path = "/run/dump1090-fa/" # path to aircraft.json file

print("==========")
print("adsb-flightalert is listening every " + str(check_delay) + " seconds for:\n")
for filter in filters:
  print(filter[0], filter[1], sep=' | ')
print("==========")

def main():
  global alert
  global already_alerted

  while True:
    scan_result = adsbflightalert.parseJSONfile(aircraft_json_path, filters)
    if (scan_result != 0): # this is where you put your alert code!
      # you could parse the returned dict to do more things here if you wanted
      # key 0 contains the count of alerted planes
      alert = True
      if not already_alerted:
        # fire off notificiations here
        print("First trigger for alert")
        already_alerted = True
      else: # do something here to update a notification?
        print("Continuing current alert")
    else: # code for no alert state here, such as cancelling a notification if one exists
      alert = False
      if already_alerted: # check if this needs cancelling
        print("Canceling alert")
        already_alerted = False

    time.sleep(check_delay) # sleep until next check

if __name__ == "__main__":
    main()
