from datetime import datetime
import json
from database.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class About(db.Model):
    __tablename__ = 'about'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='John Doe')
    title = db.Column(db.String(100), default='Full Stack Engineer')
    bio = db.Column(db.Text, nullable=True)  # Short hero intro
    description = db.Column(db.Text, nullable=True)  # Detailed description
    photo_path = db.Column(db.String(250), nullable=True)
    resume_path = db.Column(db.String(250), nullable=True)
    career_goal = db.Column(db.Text, nullable=True)
    
    # Store education, experience, and personal_info as JSON strings
    _education = db.Column('education', db.Text, default='[]')
    _experience = db.Column('experience', db.Text, default='[]')
    _personal_info = db.Column('personal_info', db.Text, default='{}')

    @property
    def education(self):
        try:
            return json.loads(self._education or '[]')
        except Exception:
            return []

    @education.setter
    def education(self, value):
        self._education = json.dumps(value)

    @property
    def experience(self):
        try:
            return json.loads(self._experience or '[]')
        except Exception:
            return []

    @experience.setter
    def experience(self, value):
        self._experience = json.dumps(value)

    @property
    def personal_info(self):
        try:
            return json.loads(self._personal_info or '{}')
        except Exception:
            return {}

    @personal_info.setter
    def personal_info(self, value):
        self._personal_info = json.dumps(value)

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    percentage = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(100), nullable=True) # Icon class (Bootstrap/FontAwesome)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(200), nullable=False) # Comma-separated list
    github_url = db.Column(db.String(250), nullable=True)
    demo_url = db.Column(db.String(250), nullable=True)
    primary_image = db.Column(db.String(250), nullable=True)
    project_file = db.Column(db.String(250), nullable=True)
    date = db.Column(db.String(50), nullable=True)
    
    # Relation for multiple secondary screenshots
    screenshots = db.relationship('ProjectScreenshot', backref='project', cascade='all, delete-orphan')

class ProjectScreenshot(db.Model):
    __tablename__ = 'project_screenshots'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    image_path = db.Column(db.String(250), nullable=False)

class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(250), nullable=True)
    pdf_path = db.Column(db.String(250), nullable=True)
    issuer = db.Column(db.String(100), nullable=True)
    date_earned = db.Column(db.String(50), nullable=True)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=True)

class Hobby(db.Model):
    __tablename__ = 'hobbies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100), nullable=True)

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(100), nullable=True)

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_role = db.Column(db.String(100), nullable=True)
    review = db.Column(db.Text, nullable=False)
    client_photo = db.Column(db.String(250), nullable=True)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

class VisitorLog(db.Model):
    __tablename__ = 'visitor_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False) # Format: YYYY-MM-DD
    ip_hash = db.Column(db.String(64), nullable=False)
    user_agent = db.Column(db.String(256), nullable=True)
