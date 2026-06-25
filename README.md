# Dynamic Portfolio CMS Website (Python & Flask)

A premium, modern, fully responsive Portfolio Website with a built-in interactive Admin CMS Dashboard. Built using Flask for the backend, SQLite for data storage, and custom CSS glassmorphism styling for the frontend.

## Key Features

- **Public Portfolio Layout**:
  - Premium Dark/Light theme toggle with smooth CSS variables transition.
  - Interactive canvas particle background and custom follow-cursor.
  - Typist writing animation.
  - Project filters based on languages/technologies.
  - Dynamic About Me, Skills, Timelines, Certificates, Hobbies, and Testimonial slides.
  - Lightbox image reviewer for certificates.
  - SEO optimized with meta descriptions, Open Graph, dynamic Sitemap, and Robots.txt.
  - Security protections (CSRF, XSS, SQLi, file validation).

- **Private Admin Dashboard**:
  - Secure session-based login at `/login` with scrypt password hashing.
  - General CMS statistics (Projects, Messages, Certificates, Skills, Visitor traffic).
  - About Me editor (dynamic draggable timelines for education and experience visual editing, profile picture, and resume uploads).
  - Interactive CRUD managers (Skills, Projects with multiple screenshots, Certificates, Hobbies, Achievements, Services, and Testimonials).
  - Searchable dashboard inbox to read, mark read, or delete contact form messages.
  - Global setting configurations (Site name, social links, contact coordinates, SMTP email alerts).

---

## Installation & Local Setup

### Prerequisites
- Python 3.8 or higher.

### 1. Clone & Navigate to project directory
Set your active editor workspace to `python-portfolio/`.

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## Administration Authentication

- **Login URL**: `http://127.0.0.1:5000/login`
- **Default Username**: `admin`
- **Default Password**: `admin123`

> [!WARNING]
> On your first successful login, please immediately visit the **Settings** panel on the right side and change the admin password to a secure value.

---

## Deployment Strategies

This CMS works perfectly on any cloud provider supporting Python and SQLite:

### 1. PythonAnywhere (Recommended for Free Hosting)
1. Upload your code files to PythonAnywhere.
2. Create a new Web App selecting **Manual Configuration** -> **Python 3.10+**.
3. Configure your WSGI configuration file under the Web tab:
   ```python
   import sys
   import os

   path = '/home/yourusername/python-portfolio'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import create_app
   application = create_app()
   ```
4. Set up your Virtual Environment path on the Web tab, reload, and view your site.

### 2. Render
1. Create a new **Web Service** linked to your Github repository.
2. Select **Python** runtime.
3. Set **Start Command**: `gunicorn "app:create_app()"`
4. Add a **Disk (Volume)** to persist SQLite database uploads. Mount path: `/instance`. Set `DATABASE_URL` env variable: `sqlite:////instance/portfolio.db`.

### 3. Railway
1. Create a new project from your Github repo.
2. Link a persistent Railway volume. Mount path: `/app/instance`.
3. Startup command is automatically detected via python requirements.
