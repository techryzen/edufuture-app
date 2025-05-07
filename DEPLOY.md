# Deploying to PythonAnywhere

1. Sign up for a free account at https://www.pythonanywhere.com/

2. Once logged in, go to the "Web" tab and click "Add a new web app"

3. Choose "Manual configuration" and select Python 3.9

4. In the "Code" section:
   - Set the working directory to your project directory
   - Set the WSGI configuration file to `/var/www/yourusername_pythonanywhere_com_wsgi.py`

5. In the "Virtualenv" section:
   - Create a new virtualenv with Python 3.9
   - Install requirements: `pip install -r requirements.txt`

6. In the "Environment variables" section, add:
   ```
   FLASK_ENV=production
   FLASK_APP=app.py
   MONGODB_URI=mongodb+srv://rishab0909:1234@cluster0.7icfipp.mongodb.net/edufuture?retryWrites=true&w=majority&appName=Cluster0
   ```

7. In the WSGI configuration file, replace the contents with:
   ```python
   import os
   import sys

   path = '/home/yourusername/yourproject'
   if path not in sys.path:
       sys.path.append(path)

   from app import create_app
   application = create_app('production')
   ```

8. Click "Reload" to start your application

Your application will be available at `yourusername.pythonanywhere.com` 