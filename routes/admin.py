import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database.db import db
from models.models import (
    User, About, Skill, Project, ProjectScreenshot, Certificate, 
    Achievement, Hobby, Service, Testimonial, Message, Setting, VisitorLog
)
from forms.forms import (
    AboutForm, SkillForm, ProjectForm, CertificateForm, 
    AchievementForm, HobbyForm, ServiceForm, TestimonialForm, SettingsForm, ChangePasswordForm
)

admin_bp = Blueprint('admin', __name__)

# File Upload Helpers
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, folder):
    """Saves file securely with a unique hash prefix to prevent duplicates."""
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
        
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    base = filename.rsplit('.', 1)[0] if '.' in filename else filename
    unique_name = f"{base}_{uuid.uuid4().hex[:8]}.{ext}"
    
    dest_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(dest_folder, exist_ok=True)
    
    file.save(os.path.join(dest_folder, unique_name))
    return f"uploads/{folder}/{unique_name}"

def remove_file(relative_path):
    """Deletes files from the disk when replaced or deleted from DB."""
    if not relative_path:
        return
    full_path = os.path.join(current_app.root_path, 'static', relative_path)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass

@admin_bp.route('/admin')
@login_required
def dashboard():
    # Gather database statistics
    total_projects = Project.query.count()
    total_messages = Message.query.count()
    unread_messages = Message.query.filter_by(is_read=False).count()
    
    about = About.query.first()
    resume_uploaded = True if about and about.resume_path else False
    
    total_certificates = Certificate.query.count()
    total_skills = Skill.query.count()
    
    visitor_counter_setting = Setting.query.filter_by(key='visitor_counter').first()
    visitor_count = int(visitor_counter_setting.value) if visitor_counter_setting else 0
    
    # Recent items
    recent_messages = Message.query.order_by(Message.timestamp.desc()).limit(5).all()
    recent_projects = Project.query.limit(5).all()
    
    # Simple chart visitor metrics (last 7 days)
    visitor_data = VisitorLog.query.order_by(VisitorLog.date.desc()).limit(15).all()
    visitor_chart = {}
    for log in reversed(visitor_data):
        visitor_chart[log.date] = visitor_chart.get(log.date, 0) + 1
        
    return render_template(
        'admin/dashboard.html',
        total_projects=total_projects,
        total_messages=total_messages,
        unread_messages=unread_messages,
        resume_uploaded=resume_uploaded,
        total_certificates=total_certificates,
        total_skills=total_skills,
        visitor_count=visitor_count,
        recent_messages=recent_messages,
        recent_projects=recent_projects,
        visitor_chart=visitor_chart
    )

# 1. Edit Profile / About Me
@admin_bp.route('/admin/about', methods=['GET', 'POST'])
@login_required
def edit_about():
    about = About.query.first()
    if not about:
        about = About()
        db.session.add(about)
        db.session.commit()

    form = AboutForm(obj=about)
    if form.validate_on_submit():
        about.name = form.name.data
        about.title = form.title.data
        about.bio = form.bio.data
        about.description = form.description.data
        about.career_goal = form.career_goal.data
        
        # Save custom JSON fields from hidden fields (processed by JS admin timeline editor)
        about._education = request.form.get('education_hidden', '[]')
        about._experience = request.form.get('experience_hidden', '[]')
        
        # Profile Photo Upload
        if form.photo.data:
            # Delete old image if exists
            remove_file(about.photo_path)
            about.photo_path = save_file(form.photo.data, 'profile')
            
        # Resume Upload
        if form.resume.data:
            remove_file(about.resume_path)
            about.resume_path = save_file(form.resume.data, 'resumes')
            
        db.session.commit()
        flash("About Me profile updated successfully!", "success")
        return redirect(url_for('admin.edit_about'))

    return render_template('admin/about.html', form=form, about=about)

@admin_bp.route('/admin/about/resume/delete', methods=['POST'])
@login_required
def delete_resume():
    about = About.query.first()
    if about and about.resume_path:
        remove_file(about.resume_path)
        about.resume_path = None
        db.session.commit()
        flash("Resume deleted successfully.", "success")
    return redirect(url_for('admin.edit_about'))

# 2. Manage Skills
@admin_bp.route('/admin/skills', methods=['GET', 'POST'])
@login_required
def skills():
    form = SkillForm()
    if form.validate_on_submit():
        skill = Skill(
            name=form.name.data,
            percentage=form.percentage.data,
            icon=form.icon.data
        )
        db.session.add(skill)
        db.session.commit()
        flash(f"Skill '{skill.name}' added successfully!", "success")
        return redirect(url_for('admin.skills'))
        
    search_query = request.args.get('search', '')
    if search_query:
        all_skills = Skill.query.filter(Skill.name.like(f"%{search_query}%")).all()
    else:
        all_skills = Skill.query.all()
        
    return render_template('admin/skills.html', form=form, skills=all_skills, search_query=search_query)

@admin_bp.route('/admin/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    flash(f"Skill '{skill.name}' has been deleted.", "success")
    return redirect(url_for('admin.skills'))

# 3. Manage Projects
@admin_bp.route('/admin/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = ProjectForm()
    if form.validate_on_submit():
        primary_img = save_file(form.primary_image.data, 'projects')
        attached_file = save_file(form.project_file.data, 'project_attachments')
        
        project = Project(
            title=form.title.data,
            description=form.description.data,
            technologies=form.technologies.data,
            github_url=form.github_url.data,
            demo_url=form.demo_url.data,
            date=form.date.data,
            primary_image=primary_img,
            project_file=attached_file
        )
        db.session.add(project)
        db.session.commit()
        
        # Save multiple secondary screenshots
        screenshot_files = request.files.getlist('screenshots')
        for file in screenshot_files:
            img_path = save_file(file, 'projects')
            if img_path:
                shot = ProjectScreenshot(project_id=project.id, image_path=img_path)
                db.session.add(shot)
        db.session.commit()
        
        flash(f"Project '{project.title}' added successfully!", "success")
        return redirect(url_for('admin.projects'))
        
    search_query = request.args.get('search', '')
    if search_query:
        all_projects = Project.query.filter(
            (Project.title.like(f"%{search_query}%")) | 
            (Project.technologies.like(f"%{search_query}%"))
        ).all()
    else:
        all_projects = Project.query.all()
        
    return render_template('admin/projects.html', form=form, projects=all_projects, search_query=search_query)

@admin_bp.route('/admin/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.technologies = form.technologies.data
        project.github_url = form.github_url.data
        project.demo_url = form.demo_url.data
        project.date = form.date.data
        
        if form.primary_image.data:
            remove_file(project.primary_image)
            project.primary_image = save_file(form.primary_image.data, 'projects')
            
        if form.project_file.data:
            remove_file(project.project_file)
            project.project_file = save_file(form.project_file.data, 'project_attachments')
            
        # Append extra screenshots if selected
        screenshot_files = request.files.getlist('screenshots')
        for file in screenshot_files:
            img_path = save_file(file, 'projects')
            if img_path:
                shot = ProjectScreenshot(project_id=project.id, image_path=img_path)
                db.session.add(shot)
                
        db.session.commit()
        flash(f"Project '{project.title}' edited successfully!", "success")
        return redirect(url_for('admin.projects'))
        
    return render_template('admin/projects_edit.html', form=form, project=project)

@admin_bp.route('/admin/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Delete related assets
    remove_file(project.primary_image)
    remove_file(project.project_file)
    for shot in project.screenshots:
        remove_file(shot.image_path)
        
    db.session.delete(project)
    db.session.commit()
    flash(f"Project '{project.title}' has been deleted.", "success")
    return redirect(url_for('admin.projects'))

@admin_bp.route('/admin/projects/<int:project_id>/screenshot/delete/<int:shot_id>', methods=['POST'])
@login_required
def delete_screenshot(project_id, shot_id):
    shot = ProjectScreenshot.query.get_or_404(shot_id)
    remove_file(shot.image_path)
    db.session.delete(shot)
    db.session.commit()
    flash("Screenshot deleted.", "success")
    return redirect(url_for('admin.edit_project', project_id=project_id))

# 4. Certificates Management
@admin_bp.route('/admin/certificates', methods=['GET', 'POST'])
@login_required
def certificates():
    form = CertificateForm()
    if form.validate_on_submit():
        img = save_file(form.image_file.data, 'certificates')
        pdf = save_file(form.pdf_file.data, 'certificates')
        
        cert = Certificate(
            title=form.title.data,
            issuer=form.issuer.data,
            date_earned=form.date_earned.data,
            image_path=img,
            pdf_path=pdf
        )
        db.session.add(cert)
        db.session.commit()
        flash(f"Certificate '{cert.title}' added successfully!", "success")
        return redirect(url_for('admin.certificates'))
        
    search_query = request.args.get('search', '')
    if search_query:
        all_certs = Certificate.query.filter(
            (Certificate.title.like(f"%{search_query}%")) |
            (Certificate.issuer.like(f"%{search_query}%"))
        ).all()
    else:
        all_certs = Certificate.query.all()
        
    return render_template('admin/certificates.html', form=form, certificates=all_certs, search_query=search_query)

@admin_bp.route('/admin/certificates/delete/<int:cert_id>', methods=['POST'])
@login_required
def delete_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    remove_file(cert.image_path)
    remove_file(cert.pdf_path)
    db.session.delete(cert)
    db.session.commit()
    flash(f"Certificate '{cert.title}' deleted.", "success")
    return redirect(url_for('admin.certificates'))

# 5. Achievements & Hobbies
@admin_bp.route('/admin/achievements', methods=['GET', 'POST'])
@login_required
def achievements():
    ach_form = AchievementForm()
    hob_form = HobbyForm()
    
    active_tab = 'achievements'
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_achievement' and ach_form.validate():
            ach = Achievement(
                title=ach_form.title.data,
                description=ach_form.description.data,
                date=ach_form.date.data
            )
            db.session.add(ach)
            db.session.commit()
            flash("Achievement added successfully!", "success")
            return redirect(url_for('admin.achievements'))
            
        elif action == 'add_hobby' and hob_form.validate():
            hob = Hobby(
                name=hob_form.name.data,
                icon=hob_form.icon.data
            )
            db.session.add(hob)
            db.session.commit()
            flash("Hobby added successfully!", "success")
            active_tab = 'hobbies'
            return redirect(url_for('admin.achievements', tab='hobbies'))
            
    all_achievements = Achievement.query.all()
    all_hobbies = Hobby.query.all()
    
    tab_param = request.args.get('tab', 'achievements')
    if tab_param in ['achievements', 'hobbies']:
        active_tab = tab_param

    return render_template(
        'admin/achievements.html', 
        ach_form=ach_form, 
        hob_form=hob_form, 
        achievements=all_achievements,
        hobbies=all_hobbies,
        active_tab=active_tab
    )

@admin_bp.route('/admin/achievements/delete/<int:ach_id>', methods=['POST'])
@login_required
def delete_achievement(ach_id):
    ach = Achievement.query.get_or_404(ach_id)
    db.session.delete(ach)
    db.session.commit()
    flash("Achievement deleted.", "success")
    return redirect(url_for('admin.achievements'))

@admin_bp.route('/admin/hobbies/delete/<int:hob_id>', methods=['POST'])
@login_required
def delete_hobby(hob_id):
    hob = Hobby.query.get_or_404(hob_id)
    db.session.delete(hob)
    db.session.commit()
    flash("Hobby deleted.", "success")
    return redirect(url_for('admin.achievements', tab='hobbies'))

# 6. Messages / Inbox
@admin_bp.route('/admin/messages')
@login_required
def messages():
    search_query = request.args.get('search', '')
    if search_query:
        all_messages = Message.query.filter(
            (Message.name.like(f"%{search_query}%")) |
            (Message.subject.like(f"%{search_query}%")) |
            (Message.message.like(f"%{search_query}%"))
        ).order_by(Message.timestamp.desc()).all()
    else:
        all_messages = Message.query.order_by(Message.timestamp.desc()).all()
        
    return render_template('admin/messages.html', messages=all_messages, search_query=search_query)

@admin_bp.route('/admin/messages/read/<int:msg_id>', methods=['POST'])
@login_required
def mark_read(msg_id):
    msg = Message.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route('/admin/messages/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted successfully.", "success")
    return redirect(url_for('admin.messages'))

# 7. System Settings
@admin_bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Load settings from db
    settings_dict = {}
    for s in Setting.query.all():
        settings_dict[s.key] = s.value

    # Load into form
    form = SettingsForm(data=settings_dict)
    change_pw_form = ChangePasswordForm()

    if form.validate_on_submit():
        for key in form.data:
            if key == 'csrf_token':
                continue
            
            # Map Boolean fields to strings
            val = form.data[key]
            if isinstance(val, bool):
                val_str = 'true' if val else 'false'
            else:
                val_str = str(val) if val is not None else ''

            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = val_str
            else:
                setting = Setting(key=key, value=val_str)
                db.session.add(setting)
                
        db.session.commit()
        flash("Settings saved successfully!", "success")
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', form=form, change_pw_form=change_pw_form)
