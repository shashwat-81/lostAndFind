from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from bson import ObjectId
from extensions import mongo
from models.notification import Notification
from utils.db_utils import get_filtered_items
from datetime import datetime

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

@items_bp.route('/items/<item_id>/claim', methods=['POST'])
@login_required
def claim_item(item_id):
    try:
        item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
        if not item:
            flash('Item not found', 'danger')
            return redirect(url_for('items.browse_items'))

        if item['status'] != 'found':
            flash('This item is not available for claiming', 'warning')
            return redirect(url_for('items.view_item', item_id=item_id))

        claim_data = {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'message': request.form.get('message'),
            'status': 'pending',
            'created_at': datetime.utcnow()
        }

        # Add claim request to item
        mongo.db.items.update_one(
            {'_id': ObjectId(item_id)},
            {'$push': {'claim_requests': claim_data}}
        )

        # Notify admin about new claim
        admin_notification = Notification(
            user_id='admin',
            message=f"New claim request for '{item['title']}' by {current_user.username}",
            item_id=item_id
        )
        admin_notification.save()

        flash('Your claim request has been submitted successfully', 'success')
        return redirect(url_for('items.view_item', item_id=item_id))

    except Exception as e:
        flash('An error occurred while processing your request', 'danger')
        return redirect(url_for('items.view_item', item_id=item_id))

@items_bp.route('/items/<item_id>/update-status', methods=['POST'])
@login_required
def update_item_status(item_id):
    if not current_user.role == 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    new_status = request.form.get('status')
    claim_id = request.form.get('claim_id')
    
    item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    updates = {'status': new_status}
    
    if claim_id:
        # Update specific claim request status
        mongo.db.items.update_one(
            {
                '_id': ObjectId(item_id),
                'claim_requests.user_id': claim_id
            },
            {'$set': {'claim_requests.$.status': 'approved' if new_status == 'claimed' else 'rejected'}}
        )
        
        # Notify the user who made the claim
        notification = Notification(
            user_id=claim_id,
            message=f"Your claim for '{item['title']}' has been {new_status}",
            item_id=item_id
        )
        notification.save()
    
    # Notify the original reporter
    reporter_notification = Notification(
        user_id=item['reporter_id'],
        message=f"Status update for your item '{item['title']}': {new_status}",
        item_id=item_id
    )
    reporter_notification.save()
    
    mongo.db.items.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': updates}
    )
    
    return jsonify({'success': True})

@items_bp.route('/items/<item_id>/claim/<claim_id>/<action>', methods=['POST'])
@login_required
def process_claim(item_id, claim_id, action):
    print(f"Processing claim: {item_id}, {claim_id}, {action}")  # Debug log
    
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        if action not in ['approve', 'reject']:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400

        item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404

        # Update claim status
        update_result = mongo.db.items.update_one(
            {
                '_id': ObjectId(item_id),
                'claim_requests.user_id': claim_id
            },
            {
                '$set': {
                    'claim_requests.$.status': action + 'd',
                    'claim_requests.$.processed_at': datetime.utcnow(),
                    'claim_requests.$.processed_by': current_user.id,
                    'status': 'claimed' if action == 'approve' else item['status']
                }
            }
        )

        if update_result.modified_count == 0:
            return jsonify({'success': False, 'message': 'No changes made'}), 400

        # Send notification
        notification = Notification(
            user_id=claim_id,
            message=f"Your claim has been {action}d",
            item_id=item_id
        ).save()

        return jsonify({
            'success': True,
            'message': f'Claim {action}d successfully'
        })

    except Exception as e:
        print(f"Error processing claim: {str(e)}")  # Debug log
        return jsonify({'success': False, 'message': str(e)}), 500

@items_bp.route('/items/<item_id>')
def view_item(item_id):
    try:
        item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
        if not item:
            flash('Item not found', 'danger')
            return redirect(url_for('items.browse_items'))
            
        return render_template('items/view_item.html', item=item)
    except Exception as e:
        flash('Error loading item', 'danger')
        return redirect(url_for('items.browse_items'))

@items_bp.route('/items/<item_id>/check-status')
@login_required
def check_item_status(item_id):
    try:
        item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
        if not item:
            return jsonify({'error': 'Item not found'}), 404
            
        # Check if user has pending claims
        user_claim = next(
            (claim for claim in item.get('claim_requests', [])
             if claim['user_id'] == str(current_user.id)),
            None
        )
        
        status_changed = False
        if user_claim and user_claim['status'] != 'pending':
            status_changed = True
            
        return jsonify({
            'status_changed': status_changed,
            'current_status': item['status']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
