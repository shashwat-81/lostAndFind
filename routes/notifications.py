from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from models.notification import Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
@login_required
def view_notifications():
    notifications = Notification.get_user_notifications(current_user.id)
    return render_template('notifications.html', notifications=notifications)

@notifications_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    Notification.mark_as_read(notification_id)
    return jsonify({'success': True})

@notifications_bp.route('/notifications/count')
@login_required
def get_unread_count():
    notifications = Notification.get_user_notifications(current_user.id)
    unread_count = sum(1 for n in notifications if not n.get('read', False))
    return jsonify({'count': unread_count})