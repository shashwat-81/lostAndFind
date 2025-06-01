from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import mongo
from functools import wraps
from datetime import datetime
from bson import ObjectId

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('general.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get filter parameters
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')

    # Build query
    query = {}
    if category:
        query['category'] = category
    if status:
        query['status'] = status
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]

    # Get statistics
    stats = {
        'total_items': mongo.db.items.count_documents({}),
        'lost_items': mongo.db.items.count_documents({'status': 'lost'}),
        'found_items': mongo.db.items.count_documents({'status': 'found'}),
        'total_users': mongo.db.users.count_documents({}),
        'recent_reports': mongo.db.items.count_documents({
            'report_date': {'$gte': datetime.now().replace(hour=0, minute=0)}
        })
    }
    
    # Get items with pagination
    page = int(request.args.get('page', 1))
    per_page = 10
    skip = (page - 1) * per_page
    
    items = list(mongo.db.items.find(query)
                .sort('report_date', -1)
                .skip(skip)
                .limit(per_page))
    
    total_items = mongo.db.items.count_documents(query)
    total_pages = (total_items + per_page - 1) // per_page

    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         items=items,
                         current_page=page,
                         total_pages=total_pages,
                         category=category,
                         status=status,
                         search=search)

@admin_bp.route('/items/<item_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_item(item_id):
    try:
        result = mongo.db.items.delete_one({'_id': ObjectId(item_id)})
        if result.deleted_count:
            return jsonify({'message': 'Item deleted successfully'}), 200
        return jsonify({'error': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/items/<item_id>/update', methods=['POST'])
@login_required
@admin_required
def update_item(item_id):
    try:
        updates = {
            'status': request.form.get('status'),
            'category': request.form.get('category'),
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'location': request.form.get('location'),
            'updated_at': datetime.utcnow(),
            'updated_by': current_user.id
        }
        
        result = mongo.db.items.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': updates}
        )
        
        if result.modified_count:
            flash('Item updated successfully', 'success')
        else:
            flash('No changes made', 'info')
            
        return redirect(url_for('admin.dashboard'))
    except Exception as e:
        flash(f'Error updating item: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = list(mongo.db.users.find())
    return render_template('admin/users.html', users=users)

@admin_bp.route('/reports')
@login_required
@admin_required
def view_reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    pipeline = [
        {
            '$group': {
                '_id': {
                    'status': '$status',
                    'category': '$category'
                },
                'count': {'$sum': 1}
            }
        }
    ]
    
    report_data = list(mongo.db.items.aggregate(pipeline))
    return render_template('admin/reports.html', report_data=report_data)
