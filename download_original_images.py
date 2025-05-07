import os
import requests
from urllib.parse import urlparse

# Create directory if it doesn't exist
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Main function to download images from URLs
def download_images():
    # Create the destination directory
    image_dir = 'app/static/images'
    ensure_dir(image_dir)
    
    # Dictionary of images to download with their URLs and destination filenames
    images = {
        # User avatars
        'user1.jpg': 'https://randomuser.me/api/portraits/women/1.jpg',
        'user2.jpg': 'https://randomuser.me/api/portraits/men/1.jpg',
        'user3.jpg': 'https://randomuser.me/api/portraits/women/2.jpg',
        
        # Main images
        'hero_image.jpg': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        'about_mission.jpg': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        
        # Team member images
        'team_member_1.jpg': 'https://randomuser.me/api/portraits/women/32.jpg',
        'team_member_2.jpg': 'https://randomuser.me/api/portraits/men/32.jpg',
        'team_member_3.jpg': 'https://randomuser.me/api/portraits/women/42.jpg',
        'team_member_4.jpg': 'https://randomuser.me/api/portraits/men/42.jpg',
        
        # Testimonial images
        'testimonial1.jpg': 'https://randomuser.me/api/portraits/men/75.jpg',
        'testimonial2.jpg': 'https://randomuser.me/api/portraits/women/75.jpg',
        'testimonial3.jpg': 'https://randomuser.me/api/portraits/men/85.jpg',
        'testimonial4.jpg': 'https://randomuser.me/api/portraits/women/85.jpg',
        
        # Blog post images
        'blog_post_1.jpg': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        'blog_post_2.jpg': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        'blog_post_3.jpg': 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        
        # Other images
        'students.jpg': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80',
        'newsletter.jpg': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1171&q=80',
        
        # Favicon should be created separately - the one we created earlier is fine
    }
    
    # Download each image
    print(f"🌐 Downloading {len(images)} images...")
    for filename, url in images.items():
        output_path = os.path.join(image_dir, filename)
        
        # Skip if the file already exists
        if os.path.exists(output_path):
            print(f"⏩ Skipping {filename} - already exists")
            continue
            
        try:
            print(f"📥 Downloading {url} to {output_path}")
            response = requests.get(url, stream=True, timeout=10)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ Downloaded {filename}")
            else:
                print(f"❌ Failed to download {filename}: Status code {response.status_code}")
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
    
    print("\n✅ Image download completed!")
    print("The images are now available in app/static/images/")
    print("Now you need to update your app/templates/index.html to use these images.")

if __name__ == "__main__":
    download_images() 