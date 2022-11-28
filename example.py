# adsb-flightalert 0.3 - example script
# search for emergency squawks and log them to stdout
import adsbflightalert
import time

alert = False # alert state
already_alerted = False # have we triggered current alert already?

check_delay = 60 # how often to check in seconds
filter_text = "7700" # should be a string because of preceding 0s
filter_type = "squawk" # one of the possible key names in each aircraft dict
aircraft_json_path = "/run/dump1090-fa/"

print("adsb-flightalert is listening for a " + filter_type + " of " + filter_text + " every " + str(check_delay) + " seconds")

def main():
  global alert
  global already_alerted

  while True:
    scan_result = adsbflightalert.parseJSONfile(aircraft_json_path, filter_text, filter_type) # returns either a dict of alerted planes with a count in key 0, or 0 if no alerts triggered

    if (scan_result != 0): # this is where you put your alert code!
      alert = True
      adsbflightalert.logAlerts(scan_result)
      if not already_alerted:
        # fire off notificiations here
        print("First trigger for alert")
        already_alerted = True
      else:
        print("Continuing current alert")
        # do something here to update a notification?
    else: # code for no alert state here, such as cancelling a notification if one exists
      alert = False
      if already_alerted: # check if this needs cancelling
        print("Canceling alert")
        already_alerted = False

    time.sleep(check_delay) # sleep until next check

if __name__ == "__main__":
    main()
