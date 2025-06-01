from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from utils.db_utils import get_filtered_items, add_item
from models.notification import Notification
from bson.objectid import ObjectId
from extensions import mongo

items_bp = Blueprint('items', __name__)

@items_bp.route('/browse')
def browse_items():
    category = request.args.get('category')
    status = request.args.get('status')
    items = get_filtered_items(category, status)
    return render_template('browse_items.html', items=items)

@items_bp.route('/report-item', methods=['GET', 'POST'])
@login_required
def report_item():
    if request.method == 'POST':
        if request.form.get('status') not in ['lost', 'found']:
            flash('Invalid status value', 'danger')
            return render_template('report_item.html')
            
        try:
            add_item(request.form, current_user)
            flash('Item reported successfully!', 'success')
            return redirect(url_for('items.browse_items'))
        except Exception as e:
            flash('Error reporting item. Please try again.', 'danger')
            return render_template('report_item.html')
            
    return render_template('report_item.html')

@items_bp.route('/items/<item_id>/update', methods=['POST'])
@login_required
def update_item(item_id):
    item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    updates = request.form.to_dict()
    
    # If status changed to 'found' and it was 'lost'
    if updates.get('status') == 'found' and item['status'] == 'lost':
        # Notify the original reporter
        notification = Notification(
            user_id=item['reporter_id'],
            message=f"Your lost item '{item['title']}' has been found!",
            item_id=item_id
        )
        notification.save()

    mongo.db.items.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': updates}
    )
    
    return jsonify({'success': True})
