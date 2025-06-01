from flask import Blueprint, render_template
from flask_login import current_user

general_bp = Blueprint('general', __name__)

@general_bp.route('/')
@general_bp.route('/home')
def home():
    return render_template('home.html')

@general_bp.route('/about')
def about():
    return render_template('about.html')
