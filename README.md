# EduFuture - Full Stack Education Consultancy Website

A modern, full-stack education consultancy website built with Flask and MongoDB. Features include user authentication, admin dashboard, and a fully functional blog system.

## Features

- **User Authentication**: Registration, login, profile management
- **Blog System**: Create, read, update, delete blog posts with comments and likes
- **Admin Panel**: Manage users, posts, and site content
- **Modern UI**: Responsive design with Tailwind CSS and Bootstrap
- **MongoDB Integration**: NoSQL database for flexible data storage

## Tech Stack

- **Backend**: Python Flask
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS, Bootstrap
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **File Uploads**: For blog images and profile pictures

## Prerequisites

- Python 3.7+
- MongoDB installed and running
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd edufuture
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Make sure MongoDB is running:
   ```
   mongod
   ```

4. Run the setup script to create necessary directories and copy static files:
   ```
   python setup.py
   ```

5. Start the application:
   ```
   python app.py
   ```

6. Navigate to `http://localhost:5000` in your browser

## Project Structure

```
edufuture/
├── app/
│   ├── models/          # Database models
│   ├── forms/           # Form classes
│   ├── routes/          # Route handlers
│   ├── templates/       # Jinja2 templates
│   └── __init__.py      # App factory
├── config/              # Configuration files
├── static/
│   ├── css/             # CSS files
│   ├── js/              # JavaScript files
│   ├── images/          # Static images
│   └── uploads/         # User uploads
├── app.py               # Application entry point
├── setup.py             # Setup script
└── README.md            # Project documentation
```

## User Roles

- **Regular Users**: Can read blog posts, comment, like, and create their own posts
- **Admin Users**: Can manage all content, users, and have access to the admin dashboard

## Default Admin Account

- **Username**: admin
- **Email**: admin@edufuture.com
- **Password**: admin123

## License

This project is available for personal and commercial use with attribution.

---

Created with ❤️ for showcase purposes 