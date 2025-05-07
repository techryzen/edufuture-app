import sys
import os

# Add the app directory to the Python path
INTERP = os.path.expanduser("/usr/local/bin/python3.8")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

# Import the app as application for Passenger
from app import create_app
application = create_app('production')

# Passenger will look for the variable "application"
from wsgiref.handlers import CGIHandler
if __name__ == '__main__':
    CGIHandler().run(application) 