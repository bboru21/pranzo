#!/bin/sh

FILE=settings/local.py

if [[ ! -e $FILE ]]; then
    echo 'Creating settings/local.py'
    touch $FILE
    echo 'from settings.base import *' > $FILE
fi

python3 -m venv venv &&
source venv/bin/activate &&
pip3 install -r requirements.txt

echo 'Setup complete'
