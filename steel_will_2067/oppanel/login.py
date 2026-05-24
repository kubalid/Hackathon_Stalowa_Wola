import sys
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR) if os.path.basename(CURRENT_DIR) == 'oppanel' else CURRENT_DIR
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from database import db
from models import User

auth_bp = Blueprint('auth', __name__, template_folder='templates')
login_manager = LoginManager()

class FlaskUser(UserMixin):
    def __init__(self, user_db_obj):
        self.id = user_db_obj.id
        self.username = user_db_obj.username
        self.role = user_db_obj.role

@login_manager.user_loader
def load_user(user_id):
    user_obj = User.query.get(int(user_id))
    if user_obj and user_obj.active:
        return FlaskUser(user_obj)
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pokaz_panel'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user_obj = User.query.filter_by(username=username).first()
        
        if user_obj and check_password_hash(user_obj.password_hash, password):
            if not user_obj.active:
                flash("To konto operatora zostało zdezaktywowane.", "error")
                return redirect(url_for('auth.login'))
                
            flask_user = FlaskUser(user_obj)
            login_user(flask_user)
            
            username_lower = user_obj.username.lower()
            if 'straz' in username_lower:
                dept_name = 'Straz_Pozarna'
            elif 'policja' in username_lower:
                dept_name = 'Policja'
            elif 'pogotowie' in username_lower:
                dept_name = 'Pogotowie'
            elif 'wojsko' in username_lower:
                dept_name = 'Wojsko'
            else:
                dept_name = 'Policja'

            session['user'] = user_obj.username
            session['dept'] = dept_name
            
            return redirect(url_for('pokaz_panel'))
        
        flash("Niepoprawny login lub hasło operatora!", "error")
        return redirect(url_for('auth.login'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    session.pop('dept', None)
    return redirect(url_for('auth.login'))