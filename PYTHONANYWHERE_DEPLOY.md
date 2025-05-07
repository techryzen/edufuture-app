# Deploying to PythonAnywhere

PythonAnywhere is a platform specifically designed for Python web applications and offers a very simple deployment process. Here's how to deploy your application:

## 1. Sign up for a free account

Go to https://www.pythonanywhere.com/ and sign up for a free account.

## 2. Upload your project files

1. Log in to PythonAnywhere
2. Go to the "Files" tab
3. Click "Upload a file" to upload your project files
   - Alternatively, you can use the "Bash console" to clone your repository:
   ```bash
   git clone https://github.com/techryzen/edufuture-app.git
   ```

## 3. Create a virtual environment

1. Go to the "Consoles" tab
2. Start a new Bash console
3. Navigate to your project directory:
   ```bash
   cd edufuture-app
   ```
4. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 4. Set up a web app

1. Go to the "Web" tab
2. Click "Add a new web app"
3. Choose "Manual Configuration"
4. Select Python 3.9
5. Enter your project path (e.g., /home/yourusername/edufuture-app)

## 5. Configure the WSGI file

1. In the "Code" section, click on the WSGI configuration file link
2. Replace the contents with this (adjust paths as needed):
   ```python
   import os
   import sys
   
   # Add your project directory to the path
   path = '/home/yourusername/edufuture-app'
   if path not in sys.path:
       sys.path.append(path)
   
   # Import your Flask app
   from app import create_app
   
   # Create the application instance
   application = create_app('production')
   ```

## 6. Add environment variables

1. In the "Web" tab, scroll down to the "Environment variables" section
2. Add these variables:
   - FLASK_ENV: production
   - MONGODB_URI: mongodb+srv://rishab0909:1234@cluster0.7icfipp.mongodb.net/edufuture?retryWrites=true&w=majority&appName=Cluster0
   - SECRET_KEY: your-secure-secret-key

## 7. Configure static files

1. In the "Web" tab, scroll down to the "Static files" section
2. Add a new mapping:
   - URL: /static/
   - Directory: /home/yourusername/edufuture-app/static/

## 8. Reload your web app

1. Click the "Reload" button at the top of the "Web" tab
2. Your app will be available at yourusername.pythonanywhere.com

## Troubleshooting

If you encounter any issues:
1. Check the error logs in the "Web" tab
2. Make sure all paths are correct in the WSGI file
3. Verify that all dependencies are installed in your virtual environment
4. Ensure MongoDB connection is working (PythonAnywhere allows outbound connections to MongoDB Atlas) 