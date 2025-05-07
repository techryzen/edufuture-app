import os
import sys

# Add the project directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the Flask application
from app import create_app

# Create the application instance
application = create_app('production') 