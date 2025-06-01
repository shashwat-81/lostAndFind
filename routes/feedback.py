from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import mongo
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def submit_feedback():
    if request.method == 'POST':
        feedback = {
            'user_id': str(current_user.id),
            'message': request.form.get('message'),
            'category': request.form.get('category', 'other'),
            'created_at': datetime.utcnow(),
            'status': 'new'
        }
        
        try:
            mongo.db.feedback.insert_one(feedback)
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('general.home'))
        except Exception as e:
            flash('Error submitting feedback. Please try again.', 'danger')
    
    return render_template('feedback.html')

@feedback_bp.route('/my-feedback')
@login_required
def view_my_feedback():
    feedbacks = mongo.db.feedback.find({'user_id': str(current_user.id)}).sort('created_at', -1)
    return render_template('my_feedback.html', feedbacks=list(feedbacks))