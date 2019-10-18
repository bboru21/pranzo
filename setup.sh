# bash

if [[ ! -e settings_local.py ]]; then
    echo 'Creating settings_local.py'
    touch settings_local.py
    echo 'from settings_base import *' > settings_local.py
fi

virtualenv virtualenv --no-site-packages && source virtualenv/bin/activate && pip install -r requirements.txt
