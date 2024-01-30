import contextlib
import os
import sys
import django
import json
import datetime
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from control.main import start_app

base_dir = os.path.dirname(__file__).replace("\\", "/")
assets_path = os.path.join(base_dir+"/", "views/ui/")
today = str(datetime.datetime.today()).replace(":","-")

if __name__ == "__main__" and len(sys.argv) > 1:
    with open(f'log.txt', 'a') as f:
        with contextlib.redirect_stdout(f):
            f.write("\n stdout ->")
            execute_from_command_line(sys.argv)
        sys.exit()

try:
    start_app(assets_path)
except Exception as err: 
    with open(f'log.txt', 'a') as f:
        f.write("\n Exception ->")
        f.write(f"\n {err}")

