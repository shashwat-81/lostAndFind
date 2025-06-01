from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.db_utils import get_filtered_items, add_item

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
