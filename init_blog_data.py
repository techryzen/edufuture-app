from app import create_app, mongo
from datetime import datetime
from bson.objectid import ObjectId
import random

app = create_app()

with app.app_context():
    # Check if posts already exist
    if mongo.db.blog_posts.count_documents({}) == 0:
        print("Initializing blog data...")
        # Get admin user
        admin = mongo.db.users.find_one({"role": "admin"})
        if not admin:
            print("Admin user not found, skipping blog post creation")
            exit()
            
        admin_id = admin["_id"]
        
        # Get categories
        categories = list(mongo.db.categories.find())
        category_ids = [str(cat["_id"]) for cat in categories]
        
        # Create 5 sample blog posts
        sample_posts = [
            {
                "title": "How to Choose the Right University",
                "slug": "how-to-choose-right-university",
                "content": "Choosing the right university is a crucial decision...",
                "category": random.choice(category_ids),
                "author_id": admin_id,
                "author_info": {
                    "username": admin["username"],
                    "profile_image": admin["profile_image"]
                },
                "tags": ["university", "education", "career"],
                "published": True,
                "featured": True,
                "views": random.randint(50, 200),
                "likes": random.randint(10, 50),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "comments": []
            },
            {
                "title": "Top Study Abroad Destinations in 2023",
                "slug": "top-study-abroad-destinations-2023",
                "content": "Studying abroad offers incredible opportunities...",
                "category": random.choice(category_ids),
                "author_id": admin_id,
                "author_info": {
                    "username": admin["username"],
                    "profile_image": admin["profile_image"]
                },
                "tags": ["study abroad", "international education"],
                "published": True,
                "featured": True,
                "views": random.randint(50, 200),
                "likes": random.randint(10, 50),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "comments": []
            },
            {
                "title": "Effective Study Techniques for Students",
                "slug": "effective-study-techniques-students",
                "content": "Developing good study habits is essential...",
                "category": random.choice(category_ids),
                "author_id": admin_id,
                "author_info": {
                    "username": admin["username"],
                    "profile_image": admin["profile_image"]
                },
                "tags": ["study tips", "learning", "education"],
                "published": True,
                "featured": False,
                "views": random.randint(50, 200),
                "likes": random.randint(10, 50),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "comments": []
            }
        ]
        
        mongo.db.blog_posts.insert_many(sample_posts)
        print(f"Created {len(sample_posts)} sample blog posts")
    else:
        print("Blog posts already exist, skipping initialization") 