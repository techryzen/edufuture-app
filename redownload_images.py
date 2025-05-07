import os
import requests

def download_image(url, filename):
    """Download an image from URL to the specified filename"""
    print(f"Downloading {url} to {filename}")
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded {filename}")
            return True
        else:
            print(f"Failed to download {filename}: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def main():
    # Images to download
    images = {
        'static/images/hero_image.jpg': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        'static/images/about_mission.jpg': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
    }
    
    # Make sure the directory exists
    os.makedirs('static/images', exist_ok=True)
    
    # Download each image
    success_count = 0
    for filename, url in images.items():
        if download_image(url, filename):
            success_count += 1
            
    print(f"\nDownloaded {success_count} of {len(images)} images.")

if __name__ == "__main__":
    main() 