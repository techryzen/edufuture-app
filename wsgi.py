import os
import sys

# Add the current directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
from app import create_app

# Create the application instance
application = create_app('production')

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port) 