# WLED-HAP

WLED Accessorie for Apple HomeKit written in python3.

## Features


* Brightness controll
* Hue controll 
* On/Off switch 
* Effect switch
* bidirectional


## Getting started 

* install required python packages using the requirements.txt
* Set up WLED (see https://github.com/Aircoookie/WLED)
* configure WLED IP and location of config.json in smart_home.py
* Generate some effects using the WLED web interface and copy the api call to the config.json

## Further stuff

* copy the smarthome.service file to /etc/systemd/system in order to start and stop the programm using systemctl (small configurations needed in the file)

