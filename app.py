import os
from datetime import date
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from database.db import init_db
from models.models import User
from routes.main import main_bp
from routes.auth import auth_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CSRF Protection
    csrf = CSRFProtect(app)

    # Initialize Database & Run Seed
    init_db(app)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # Injected context processors
    @app.context_processor
    def inject_globals():
        return {
            'date': date
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        from models.models import Setting
        socials = {}
        theme = 'dark'
        try:
            for key in ['contact_email', 'site_name']:
                s = Setting.query.filter_by(key=key).first()
                socials[key] = s.value if s else ''
            
            theme_default = Setting.query.filter_by(key='theme_default').first()
            if theme_default:
                theme = theme_default.value
        except Exception:
            pass # Fallback to empty socials and dark theme if DB is not ready
            
        return render_template('404.html', socials=socials, theme=theme), 404

    return app

if __name__ == '__main__':
    app = create_app()
    # Runs locally on http://127.0.0.1:5000
    app.run(debug=True)
