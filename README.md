# Pranzo

A Python 3 script for reading the Department of Consumer and Regulatory Affairs monthly Mobile Roadway Vehicle (MRV) Vending Lottery Results.

TLDR: Gets the DC Food Truck Schedule and downloads it as a readable spreadsheet.

## Requirements
* Python 3
* Mozilla Firefox Browser
* The appropriate Gecko driver for your computer's operating system, dowloaded from https://github.com/mozilla/geckodriver/releases, un-carchived and moved to the root directory of this script

## A Note on Python 3
Currently this script is predicated on the host computer having python3 and pip3 references to Python 3 available. In the future, those refrences will be updated to python/pip once Python 2 reaches it's end of life.

## Setup
* Run the following  to setup the VirtualEnvironment for the first time:
```
sh setup.sh
```

## Run Script
Run the following to activate the VirtualEnvironment, and kick off the Python script:
```
sh runscript.sh
```

Or alternatively, you can run the Python command yourself:
```
source venv/bin/activate && python3 pranzo.py
```

That's it for optaining the schedule via Excel Spreadsheet. If you want more, read on!

## Pranzo Database
Intended for creating a database to associate data with specific Food Trucks, such as reviews and truck names that deviate from that of the spreadsheet.

### Setup Database
Run the following to setup the initial database:
```
python3 models.py --settings=settings.base
```
