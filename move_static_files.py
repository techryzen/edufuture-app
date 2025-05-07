import os
import shutil

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def move_static_files():
    """Move static files from app/static to static directory"""
    source_dir = 'app/static'
    target_dir = 'static'
    
    # Ensure target directories exist
    ensure_dir(os.path.join(target_dir, 'css'))
    ensure_dir(os.path.join(target_dir, 'js'))
    ensure_dir(os.path.join(target_dir, 'images'))
    
    # Move CSS files
    css_source = os.path.join(source_dir, 'css')
    css_target = os.path.join(target_dir, 'css')
    if os.path.exists(css_source):
        print(f"Moving CSS files from {css_source} to {css_target}")
        for file_name in os.listdir(css_source):
            source_file = os.path.join(css_source, file_name)
            target_file = os.path.join(css_target, file_name)
            if os.path.isfile(source_file):
                shutil.copy2(source_file, target_file)
                print(f"Copied {file_name}")
    
    # Move JS files
    js_source = os.path.join(source_dir, 'js')
    js_target = os.path.join(target_dir, 'js')
    if os.path.exists(js_source):
        print(f"Moving JS files from {js_source} to {js_target}")
        for file_name in os.listdir(js_source):
            source_file = os.path.join(js_source, file_name)
            target_file = os.path.join(js_target, file_name)
            if os.path.isfile(source_file):
                shutil.copy2(source_file, target_file)
                print(f"Copied {file_name}")
    
    # Move image files
    img_source = os.path.join(source_dir, 'images')
    img_target = os.path.join(target_dir, 'images')
    if os.path.exists(img_source):
        print(f"Moving image files from {img_source} to {img_target}")
        for file_name in os.listdir(img_source):
            source_file = os.path.join(img_source, file_name)
            target_file = os.path.join(img_target, file_name)
            if os.path.isfile(source_file):
                shutil.copy2(source_file, target_file)
                print(f"Copied {file_name}")
            elif os.path.isdir(source_file):
                # Handle subdirectories if needed
                subdir_target = os.path.join(img_target, file_name)
                ensure_dir(subdir_target)
                for subfile in os.listdir(source_file):
                    sub_source = os.path.join(source_file, subfile)
                    sub_target = os.path.join(subdir_target, subfile)
                    if os.path.isfile(sub_source):
                        shutil.copy2(sub_source, sub_target)
                        print(f"Copied {file_name}/{subfile}")
    
    print("\nAll static files have been moved successfully!")

if __name__ == "__main__":
    move_static_files() 