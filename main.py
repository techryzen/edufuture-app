import os
import sys

# Add the current directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import from the app module and export as 'app'
from app import create_app

# Create the application instance for production
app = create_app('production') 