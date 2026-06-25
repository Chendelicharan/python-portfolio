from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database.db import db
from models.models import User
from forms.forms import LoginForm, ChangePasswordForm, ForgotPasswordForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        print(f"Login attempt - Username: '{form.username.data}', Password: '{form.password.data}'")
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            print(f"User found in DB. Email: {user.email}")
            check = user.check_password(form.password.data)
            print(f"Password check result: {check}")
            if check:
                login_user(user, remember=form.remember.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash("Logged in successfully!", "success")
                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin.dashboard'))
            else:
                flash("Invalid username or password.", "danger")
        else:
            print(f"User '{form.username.data}' NOT found in DB.")
            flash("Invalid username or password.", "danger")
    else:
        if request.method == 'POST':
            print("WTForms Validation Errors:", form.errors)
            
    return render_template('admin/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for('admin.settings'))
        else:
            flash("Incorrect current password.", "danger")
            
    # Redirect back to settings page, carrying errors if any
    return render_template('admin/settings.html', change_pw_form=form, form=None) # Settings route handles rendering config

import string
import secrets

def send_reset_email(user_email, temp_pass):
    from models.models import Setting
    
    host = Setting.query.filter_by(key='smtp_host').first()
    port = Setting.query.filter_by(key='smtp_port').first()
    user = Setting.query.filter_by(key='smtp_user').first()
    passwd = Setting.query.filter_by(key='smtp_pass').first()
    sender = Setting.query.filter_by(key='smtp_sender').first()
    
    if not (host and port and user and passwd and sender) or not (host.value and port.value and user.value and passwd.value and sender.value):
        return False
        
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = sender.value
        msg['To'] = user_email
        msg['Subject'] = "Portfolio CMS: Administrator Password Reset"
        
        body = f"""
You requested a password reset for your Portfolio Website Administrator Dashboard.

Your new temporary password is:

-----------------------------
{temp_pass}
-----------------------------

Please log in immediately at your dashboard and update your password in the Settings page.
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(host.value, int(port.value))
        server.starttls()
        server.login(user.value, passwd.value)
        server.sendmail(sender.value, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP reset email failed: {e}")
        return False

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate a secure 10-character temporary password
            alphabet = string.ascii_letters + string.digits
            temp_pass = ''.join(secrets.choice(alphabet) for _ in range(10))
            
            # Save new hashed password
            user.set_password(temp_pass)
            db.session.commit()
            
            # Try sending the email
            sent = send_reset_email(user.email, temp_pass)
            if sent:
                flash("A new temporary password has been sent to your email address.", "success")
            else:
                # Print to terminal in case SMTP is not set up
                print("\n" + "="*50)
                print("PASSWORD RESET FALLBACK")
                print(f"For User: {user.username} ({user.email})")
                print(f"New Temporary Password: {temp_pass}")
                print("="*50 + "\n")
                flash("Password reset triggered! However, SMTP was not configured. Check your server terminal logs for the temporary password.", "warning")
            return redirect(url_for('auth.login'))
        else:
            flash("No account associated with that email address found.", "danger")
            
    return render_template('admin/forgot_password.html', form=form)
