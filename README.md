# adsb-flightalert 0.5

This little (very experimental, tell me about all the awful bugs 
in my beginner-level code!) Python module will let you parse an 
aircraft.json file from a running dump1090 instance and return a 
list with all flights that match certain criteria. Right now only 
exact matches are supported.

I found plenty of scripts and apps for parsing data from the APIs 
of flight tracker websites, but nothing for really digging into 
locally-received data and triggering an alert.

You can filter based on any key found in an aircraft record. For 
example:

* squawk = 7700
* callsign = blah
* ...or any other key used in aircraft.json!

You can also specify a (single, right now) geofence box by 
specifying a pair of coordinates in a list, bottom-left then 
top-right coordinate.

There is one main function, parseJSONfile() - send it two 
variables:

* a string with the path to the aircraft.json file including trailing slash 
(like /run/dump1090-fa/ for example)
* a list containing tuples of string pairs in the form: ("filter 
key", "search text") - note: area search needs a list and not a string.

An example script is provided to show how to use it with some 
basic logic to help suppress alert spam. You should get an idea 
of how to use the library with it. Basically you want to set up 
a main loop, sleep for a time delay (check as often as you deem 
necessary), set a variable with the results of the parsing 
function and then do what you want with the returned data. Use 
your imagination! The example logs to STDOUT.
