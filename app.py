from app import create_app
import os
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run the Flask application')
parser.add_argument('--port', type=int, default=8081, help='Port to run the app on')
args = parser.parse_args()

# Get configuration mode from environment or default to development
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    debug = config_name == 'development'
    port = int(os.environ.get('PORT', args.port))
    app.run(host='0.0.0.0', port=port, debug=debug) 