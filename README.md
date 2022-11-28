# adsb-flightalert

This little module will let you parse an aircraft.json file from a running dump1090 instance and return a list that match a certain criteria.

You can filter based on any key found in an aircraft record. For example

squawk = 7700 or callsign = blah

There is one main function, parseJSONfile() - send it three strings:

* the path to the aircraft.json file including trailing slash
* the filter text to search for, such as "7700"
* the key name to search in, such as "squawk"

Hits are logged to stdout every time they are detected right now. I may change this.

An example script is provided to show how to use it with some basic logic to help suppress alert spam. You should get an idea of how to use the library with it.
