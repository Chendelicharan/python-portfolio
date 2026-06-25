from datetime import date
from hashlib import sha256
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, send_from_directory
from database.db import db
from models.models import (
    About, Skill, Project, Certificate, Achievement, 
    Hobby, Service, Testimonial, Message, Setting, VisitorLog
)
from forms.forms import ContactForm

main_bp = Blueprint('main', __name__)

def log_visitor():
    """Hashed IP visitor logger to prevent duplicates per day."""
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1')
        ip_hash = sha256(ip.encode('utf-8')).hexdigest()
        today = date.today().strftime('%Y-%m-%d')
        
        # Check if visitor logged today
        logged = VisitorLog.query.filter_by(date=today, ip_hash=ip_hash).first()
        if not logged:
            log = VisitorLog(date=today, ip_hash=ip_hash, user_agent=request.user_agent.string[:256])
            db.session.add(log)
            
            # Increment visitor counter settings
            counter = Setting.query.filter_by(key='visitor_counter').first()
            if counter:
                try:
                    counter.value = str(int(counter.value) + 1)
                except ValueError:
                    counter.value = '1'
            else:
                db.session.add(Setting(key='visitor_counter', value='1'))
            db.session.commit()
    except Exception as e:
        print(f"Error logging visitor: {e}")

def send_notification_email(msg_obj):
    """SMTP email sender using DB settings."""
    enabled = Setting.query.filter_by(key='email_notifications').first()
    if not enabled or enabled.value.lower() != 'true':
        return False
        
    host = Setting.query.filter_by(key='smtp_host').first()
    port = Setting.query.filter_by(key='smtp_port').first()
    user = Setting.query.filter_by(key='smtp_user').first()
    passwd = Setting.query.filter_by(key='smtp_pass').first()
    sender = Setting.query.filter_by(key='smtp_sender').first()
    contact = Setting.query.filter_by(key='contact_email').first()
    
    if not (host and port and user and passwd and sender and contact) or not (host.value and port.value and user.value and passwd.value and sender.value and contact.value):
        print("SMTP credentials incomplete. Cannot send email.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = sender.value
        msg['To'] = contact.value
        msg['Subject'] = f"Portfolio Message Alert: {msg_obj.subject}"
        
        body = f"""
You have received a new contact form message on your Portfolio Website:

From: {msg_obj.name} ({msg_obj.email})
Date: {msg_obj.timestamp}
Subject: {msg_obj.subject}

Message:
-----------------------------
{msg_obj.message}
-----------------------------
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(host.value, int(port.value))
        server.starttls()
        server.login(user.value, passwd.value)
        server.sendmail(sender.value, contact.value, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP sending failed: {e}")
        return False

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    log_visitor()
    
    form = ContactForm()
    if form.validate_on_submit():
        # Save message
        message = Message(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        
        # Try sending email
        send_notification_email(message)
        
        flash("Thank you! Your message has been sent successfully.", "success")
        return redirect(url_for('main.index') + '#contact')
        
    about = About.query.first()
    skills = Skill.query.all()
    projects = Project.query.all()
    certificates = Certificate.query.all()
    achievements = Achievement.query.all()
    hobbies = Hobby.query.all()
    services = Service.query.all()
    testimonials = Testimonial.query.all()
    
    # Query theme settings
    theme_default = Setting.query.filter_by(key='theme_default').first()
    theme = theme_default.value if theme_default else 'dark'
    
    # Social URLs and Contacts
    socials = {}
    for key in ['facebook_url', 'twitter_url', 'github_url', 'linkedin_url', 'instagram_url', 'phone_number', 'contact_email', 'address', 'google_maps_embed', 'site_name']:
        s = Setting.query.filter_by(key=key).first()
        socials[key] = s.value if s else ''

    return render_template(
        'index.html',
        form=form,
        about=about,
        skills=skills,
        projects=projects,
        certificates=certificates,
        achievements=achievements,
        hobbies=hobbies,
        services=services,
        testimonials=testimonials,
        theme=theme,
        socials=socials
    )

@main_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    
    socials = {}
    for key in ['github_url', 'linkedin_url', 'contact_email', 'site_name']:
        s = Setting.query.filter_by(key=key).first()
        socials[key] = s.value if s else ''

    return render_template('project_detail.html', project=project, socials=socials)

@main_bp.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /login/\nSitemap: " + request.url_root + "sitemap.xml"
    return Response(content, mimetype="text/plain")

@main_bp.route('/sitemap.xml')
def sitemap():
    pages = []
    # Add home page
    pages.append({'loc': request.url_root, 'lastmod': date.today().strftime('%Y-%m-%d'), 'priority': '1.0'})
    
    # Add project pages
    projects = Project.query.all()
    for proj in projects:
        pages.append({
            'loc': request.url_root + 'project/' + str(proj.id),
            'lastmod': date.today().strftime('%Y-%m-%d'),
            'priority': '0.8'
        })
        
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    return Response(sitemap_xml, mimetype="application/xml")
