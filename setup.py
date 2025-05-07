import os
import shutil

def setup_directories():
    """Create necessary directories for the Flask app, ensuring they are inside the 'app' folder where relevant."""
    dirs = [
        'app/static/css',
        'app/static/js',
        'app/static/images',
        'app/static/uploads',
        'app/static/uploads/blog',
        'app/static/uploads/profile_pics',
        'app/templates/auth',
        'app/templates/blog',
        'app/templates/main',
        'app/templates/admin',
    ]
    
    print("Creating application directories...")
    for directory in dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"  ✅ Ensured directory exists: {directory}")
        except OSError as e:
            print(f"  ❌ Error creating directory {directory}: {e}")
    print("-" * 30)

def copy_static_files():
    """Copy static assets (CSS, JS, Images) from project root to app/static/"""
    
    # Define source (project root) and destination (app/static)
    source_base = '.' 
    dest_base = 'app/static'

    assets_to_copy = {
        "CSS": {"source": "css", "dest": "css"},
        "JS": {"source": "js", "dest": "js"},
        "Images": {"source": "images", "dest": "images"}
    }

    print("Copying static assets...")
    for asset_type, paths in assets_to_copy.items():
        source_dir = os.path.join(source_base, paths["source"])
        dest_dir = os.path.join(dest_base, paths["dest"])

        if os.path.exists(source_dir) and os.path.isdir(source_dir):
            try:
                # Ensure destination base directory (app/static) exists
                if not os.path.exists(dest_base):
                    os.makedirs(dest_base, exist_ok=True)
                    print(f"  ℹ️ Created base static directory: {dest_base}")

                # Copy the entire directory tree
                shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                print(f"  ✅ Copied {asset_type} from '{source_dir}' to '{dest_dir}'")
            except Exception as e:
                print(f"  ❌ Error copying {asset_type} from '{source_dir}' to '{dest_dir}': {e}")
        else:
            print(f"  ⚠️ Source {asset_type} directory not found or is not a directory: '{source_dir}' (Skipping)")
    print("-" * 30)

if __name__ == "__main__":
    print("🚀 Setting up EduFuture application...")
    print("-" * 30)
    
    # First, ensure there isn't a 'static' directory at the root from previous incorrect runs.
    # It's safer for the user to manually delete this if it exists and contains important data.
    # We will just warn if it's present.
    if os.path.exists('static') and os.path.isdir('static') and not os.path.samefile('.', 'static') and 'app' not in os.path.abspath('static'):
        # Heuristic to check if it's a root-level 'static' and not 'app/static' or similar
        # This check might not be perfect for all edge cases.
        is_likely_root_static = True
        try:
            # A more robust check: is 'app/static' inside this 'static' dir? if so, it's not the one we want.
             if os.path.commonpath([os.path.abspath('static'), os.path.abspath('app/static')]) == os.path.abspath('static') and os.path.abspath('static') != os.path.abspath('app/static'):
                pass # This is fine, app/static is inside static
             elif os.path.abspath('static') == os.path.abspath('app/static'):
                is_likely_root_static = False # It IS app/static
        except ValueError: # commonpath might raise error if paths are on different drives
            pass

        if is_likely_root_static and 'app' not in os.listdir('static'): # if 'app' folder is not inside this static folder.
             print("🤚 WARNING: A 'static' directory exists at the project root.")
             print("   This script will copy assets into 'app/static/'.")
             print("   Please ensure the root 'static/' directory is removed or backed up if it's from an old setup.")
             print("-" * 30)


    setup_directories()
    copy_static_files()
    
    print("🎉 Setup complete!")
    print("-" * 30)
    print("Next steps:")
    print("1. Ensure MongoDB is running (e.g., `brew services start mongodb-community` or `mongod`)")
    print("2. Run the Flask application: python app.py")
    print("3. Open your browser to http://127.0.0.1:5000")
    print("-" * 30) 