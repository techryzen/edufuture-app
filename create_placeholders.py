import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io

def download_placeholder(width, height, text, output_path):
    """Download a placeholder image from placehold.co or create a simple one with PIL"""
    try:
        # First try with placeholders.jpgcreator.com
        url = f"https://placeholders.jpgcreator.com/{width}x{height}.jpg?text={text}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Created {output_path} from web service")
            return True
    except Exception as e:
        print(f"⚠️ Could not download from web service: {e}")
    
    # Fallback: Create a basic placeholder with PIL
    try:
        img = Image.new('RGB', (width, height), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle(
            [(0, 0), (width-1, height-1)],
            outline=(150, 150, 150),
            width=2
        )
        
        # Add text 
        font_size = min(width, height) // 10
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
        position = ((width - text_width) // 2, (height - text_height) // 2)
        
        draw.text(
            position,
            text,
            fill=(100, 100, 100),
            font=font
        )
        
        img.save(output_path)
        print(f"✅ Created {output_path} locally with PIL")
        return True
    except Exception as e:
        print(f"❌ Error creating image with PIL: {e}")
        return False

def create_favicon(output_path):
    """Create a simple favicon"""
    try:
        img = Image.new('RGB', (32, 32), color=(59, 130, 246))  # primary blue color
        draw = ImageDraw.Draw(img)
        
        # Draw 'E' letter
        draw.text((8, 6), "E", fill=(255, 255, 255))
        
        # Convert to ICO and save
        img.save(output_path.replace('.ico', '.png'))
        
        # Convert the PNG to ICO using PIL
        favicon = Image.open(output_path.replace('.ico', '.png'))
        favicon.save(output_path)
        
        # Clean up temporary PNG
        os.remove(output_path.replace('.ico', '.png'))
        
        print(f"✅ Created favicon at {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating favicon: {e}")
        return False

def main():
    """Create all placeholder images needed for the EduFuture website"""
    # Create target directory if it doesn't exist
    images_dir = 'app/static/images'
    os.makedirs(images_dir, exist_ok=True)

    # List of images to create
    placeholders = [
        # User avatars - small circular images
        {'path': 'placeholder_user1.jpg', 'width': 200, 'height': 200, 'text': 'User 1'},
        {'path': 'placeholder_user2.jpg', 'width': 200, 'height': 200, 'text': 'User 2'},
        {'path': 'placeholder_user3.jpg', 'width': 200, 'height': 200, 'text': 'User 3'},
        
        # Hero and about images - larger images
        {'path': 'hero_image.jpg', 'width': 1200, 'height': 800, 'text': 'Hero Image'},
        {'path': 'about_mission.jpg', 'width': 1200, 'height': 800, 'text': 'About Us'},
        
        # Team member images
        {'path': 'team_member_1.jpg', 'width': 400, 'height': 400, 'text': 'Sarah Johnson'},
        {'path': 'team_member_2.jpg', 'width': 400, 'height': 400, 'text': 'Michael Chen'},
        {'path': 'team_member_3.jpg', 'width': 400, 'height': 400, 'text': 'Jessica Williams'},
        {'path': 'team_member_4.jpg', 'width': 400, 'height': 400, 'text': 'David Lee'},
        
        # Student testimonial images
        {'path': 'student_1.jpg', 'width': 200, 'height': 200, 'text': 'Priya S.'},
        {'path': 'student_2.jpg', 'width': 200, 'height': 200, 'text': 'Ahmed K.'},
        {'path': 'student_3.jpg', 'width': 200, 'height': 200, 'text': 'Chloe D.'},
        
        # Blog post images
        {'path': 'blog_post_1.jpg', 'width': 800, 'height': 400, 'text': 'Blog Post 1'},
        {'path': 'blog_post_2.jpg', 'width': 800, 'height': 400, 'text': 'Blog Post 2'},
        {'path': 'blog_post_3.jpg', 'width': 800, 'height': 400, 'text': 'Blog Post 3'},
    ]
    
    print(f"🖼️ Creating {len(placeholders)} placeholder images...")
    for placeholder in placeholders:
        output_path = os.path.join(images_dir, placeholder['path'])
        download_placeholder(
            placeholder['width'], 
            placeholder['height'], 
            placeholder['text'], 
            output_path
        )
    
    # Create favicon.ico
    create_favicon(os.path.join(images_dir, 'favicon.ico'))
    
    print("\n✅ Done! Placeholder images have been created in the app/static/images directory.")
    print("   Remember to replace these placeholders with real images for production use.")

if __name__ == "__main__":
    main() 