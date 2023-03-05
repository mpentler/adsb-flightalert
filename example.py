# adsb-flightalert 0.5 - example script
# parse a running dump1090-whatever install's aircraft.json for particular criteria in a key
# for example squawk = 7700, flight = blah, etc
import adsbflightalert
import time
import smtplib
import socket

def logAlerts(alerted_aircraft): # send to stdout
  # add time/date to log? if running as service there is no need
  # if not then it would be useful. can i detect which somehow?
  num_of_alerts = alerted_aircraft[0]

  while num_of_alerts > 0:
    print(alerted_aircraft[num_of_alerts]['matched'], "alert for - Hex:", alerted_aircraft[num_of_alerts]['hex'], "Squawk:", alerted_aircraft[num_of_alerts]['squawk'], "Callsign:", alerted_aircraft[num_of_alerts]['flight'])
    num_of_alerts -= 1

def main():
  global alert
  global already_alerting

  start_time = time.time()

  while True:
    current_time = time.time()

    if current_time > start_time + check_delay:
      scan_result = adsbflightalert.parseJSONfile(aircraft_json_path, filters)

      if (scan_result != 0): # this is where you put your alert code!
        alert = True
        if not already_alerting:
          # fire off notificiations here
          print("Triggering alert state")
          already_alerting = True
          logAlerts(scan_result) # display the alerted flights
        else: # do something here to update a notification?
         # you could check alerted hex codes against a list, for example,
         # so you don't alert planes more than neccesary, only showing new planes,
         # or skip all alert actions entirely if already in alert mode
         print("Continuing current alert state")
      else: # code for no alert state here, such as cancelling a notification if one exists
        alert = False
        if already_alerting: # check if this needs cancelling
          print("Canceling alert state")
          already_alerting = False
          # unlight an LED, change a display, etc
      start_time = current_time

    time.sleep(1)

alert = False # alert state
already_alerting = False # have we triggered an alert already?
check_delay = 10 # how often to check in seconds

aircraft_json_path = "/run/dump1090-fa/" # path to aircraft.json file
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
