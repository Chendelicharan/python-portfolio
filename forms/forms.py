from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, TextAreaField, 
    IntegerField, MultipleFileField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional, URL, NumberRange
)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message="New password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwords must match.")
    ])

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=4, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=5000)])

class AboutForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    title = StringField('Professional Title', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('Short Intro / Bio', validators=[Optional(), Length(max=500)])
    description = TextAreaField('About Me Description', validators=[Optional()])
    career_goal = TextAreaField('Career Goal', validators=[Optional()])
    photo = FileField('Profile Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    resume = FileField('Resume Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'docx', 'zip'], 'PDF, DOCX, or ZIP files only!')
    ])

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired(), Length(max=50)])
    percentage = IntegerField('Percentage', validators=[
        DataRequired(), 
        NumberRange(min=0, max=100, message="Percentage must be between 0 and 100.")
    ])
    icon = StringField('Icon Class (FontAwesome / Devicon)', validators=[Optional(), Length(max=100)])

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Project Description', validators=[DataRequired()])
    technologies = StringField('Technologies (Comma-separated)', validators=[DataRequired(), Length(max=200)])
    github_url = StringField('GitHub Link', validators=[Optional(), Length(max=250)])
    demo_url = StringField('Live Demo Link', validators=[Optional(), Length(max=250)])
    primary_image = FileField('Primary Card Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    project_file = FileField('Project File (Optional Attachment)', validators=[
        Optional(),
        FileAllowed(['zip', 'pdf', 'docx'], 'ZIP, PDF, or DOCX only!')
    ])
    screenshots = MultipleFileField('Project Screenshots (Multi-upload)', validators=[Optional()])
    date = StringField('Completion Date (e.g. June 2026)', validators=[Optional(), Length(max=50)])

class CertificateForm(FlaskForm):
    title = StringField('Certificate Name', validators=[DataRequired(), Length(max=200)])
    issuer = StringField('Issuing Organization', validators=[Optional(), Length(max=100)])
    date_earned = StringField('Date Earned (e.g. May 2026)', validators=[Optional(), Length(max=50)])
    image_file = FileField('Certificate Image Badge', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    pdf_file = FileField('Full PDF Certificate', validators=[
        Optional(),
        FileAllowed(['pdf'], 'PDF documents only!')
    ])

class AchievementForm(FlaskForm):
    title = StringField('Achievement Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    date = StringField('Date Received', validators=[Optional(), Length(max=50)])

class HobbyForm(FlaskForm):
    name = StringField('Hobby Name', validators=[DataRequired(), Length(max=100)])
    icon = StringField('Icon Class (FontAwesome / Bootstrap Icons)', validators=[Optional(), Length(max=100)])

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Service Description', validators=[Optional()])
    icon = StringField('Icon Class', validators=[Optional(), Length(max=100)])

class TestimonialForm(FlaskForm):
    client_name = StringField('Client Name', validators=[DataRequired(), Length(max=100)])
    client_role = StringField('Client Designation/Role', validators=[Optional(), Length(max=100)])
    review = TextAreaField('Testimonial Content', validators=[DataRequired()])
    client_photo = FileField('Client Avatar', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

class SettingsForm(FlaskForm):
    site_name = StringField('Site Title', validators=[DataRequired(), Length(max=150)])
    theme_default = StringField('Default Theme', validators=[DataRequired(), Length(max=10)])
    
    # Social Links
    facebook_url = StringField('Facebook Profile URL', validators=[Optional(), Length(max=250)])
    twitter_url = StringField('Twitter/X Profile URL', validators=[Optional(), Length(max=250)])
    github_url = StringField('GitHub Profile URL', validators=[Optional(), Length(max=250)])
    linkedin_url = StringField('LinkedIn Profile URL', validators=[Optional(), Length(max=250)])
    instagram_url = StringField('Instagram Profile URL', validators=[Optional(), Length(max=250)])
    
    # Contact Info
    phone_number = StringField('Display Phone Number', validators=[Optional(), Length(max=50)])
    contact_email = StringField('Display Contact Email', validators=[Optional(), Email(), Length(max=120)])
    address = StringField('Display Office / Home Address', validators=[Optional(), Length(max=200)])
    google_maps_embed = TextAreaField('Google Maps Embed URL / Link', validators=[Optional()])
    
    # Notification & SMTP
    email_notifications = BooleanField('Enable Message Email Alerts')
    smtp_host = StringField('SMTP Server Host', validators=[Optional(), Length(max=100)])
    smtp_port = IntegerField('SMTP Server Port', validators=[Optional(), NumberRange(min=1, max=65535)])
    smtp_user = StringField('SMTP Username / Email', validators=[Optional(), Length(max=120)])
    smtp_pass = PasswordField('SMTP Password', validators=[Optional()])
    smtp_sender = StringField('Sender Address (From)', validators=[Optional(), Length(max=120)])

class ForgotPasswordForm(FlaskForm):
    email = StringField('Registered Email Address', validators=[DataRequired(), Email(), Length(max=120)])

