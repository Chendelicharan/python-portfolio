import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize the database and create tables if they do not exist."""
    db.init_app(app)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    with app.app_context():
        db.create_all()
        seed_database()

def seed_database():
    """Seed default database values for user, about, and settings."""
    from models.models import User, About, Setting
    
    # Seed User if empty
    if not User.query.first():
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Database Seed: Created default admin user ('admin' / 'admin123')")

    # Seed About if empty
    if not About.query.first():
        about = About(
            name="John Doe",
            title="Full Stack Software Engineer",
            bio="Passionate engineer building elegant web solutions and robust architectures.",
            description="I am a software engineer with years of experience building applications using Python, Javascript, and modern frameworks. I focus on creating clean, maintainable code and premium user experiences.",
            career_goal="To work on challenging, high-impact software systems while pushing the boundaries of web engineering.",
            education=[
                {
                    "institution": "Stanford University",
                    "degree": "B.S. Computer Science",
                    "years": "2018 - 2022",
                    "details": "Specialized in Software Systems. Graduated with honors."
                }
            ],
            experience=[
                {
                    "company": "Tech Innovations Inc.",
                    "role": "Senior Software Engineer",
                    "years": "2024 - Present",
                    "details": "Lead a team of 4 engineers building Flask/React microservices. Optimized API performance by 40%."
                },
                {
                    "company": "Startup Hub",
                    "role": "Full Stack Engineer",
                    "years": "2022 - 2024",
                    "details": "Built responsive dashboard features, scaled database queries, and implemented real-time notifications."
                }
            ],
            personal_info={
                "Age": "26",
                "Residence": "USA",
                "Freelance": "Available",
                "Address": "Silicon Valley, CA"
            }
        )
        db.session.add(about)
        print("Database Seed: Created default About information.")

    # Seed Settings if empty
    default_settings = {
        'site_name': 'My Premium Portfolio',
        'theme_default': 'dark',
        'email_notifications': 'false',
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': '587',
        'smtp_user': '',
        'smtp_pass': '',
        'smtp_sender': '',
        'facebook_url': 'https://facebook.com',
        'twitter_url': 'https://twitter.com',
        'github_url': 'https://github.com',
        'linkedin_url': 'https://linkedin.com',
        'instagram_url': 'https://instagram.com',
        'phone_number': '+1 (555) 019-2834',
        'contact_email': 'contact@example.com',
        'address': 'San Francisco, CA',
        'google_maps_embed': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3153.0863073740263!2d-122.41941550000001!3d37.7749295!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x80859a6d00690021%3A0x4a501367f076adff!2sSan+Francisco%2C+CA!5e0!3m2!1sen!2sus!4v1565265434567!5m2!1sen!2sus',
        'visitor_counter': '0'
    }

    for key, val in default_settings.items():
        if not Setting.query.filter_by(key=key).first():
            setting = Setting(key=key, value=val)
            db.session.add(setting)
            
    db.session.commit()
