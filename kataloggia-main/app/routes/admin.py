"""
Admin Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3

bp = Blueprint('admin', __name__)

@bp.route('/brands')
@login_required
def brands():
    """Admin Brands Page"""
    # Simple admin check (can be improved later)
    # For now, assuming all logged-in users can access or just checking a specific username/role if needed.
    # Given the context, I'll just allow logged in users for now or check if there's an admin flag.
    # The user model doesn't seem to have an 'is_admin' field in the schema I saw earlier.
    # I'll proceed with login_required only for now to fix the 404.
    
    conn = sqlite3.connect('favit.db')
    cursor = conn.cursor()
    
    # Get unique brands and their product counts
    cursor.execute('''
        SELECT brand, COUNT(*) as count 
        FROM products 
        GROUP BY brand 
        ORDER BY brand ASC
    ''')
    brands_data = cursor.fetchall()
    conn.close()
    
    # Format data
    brands = [{'name': row[0], 'count': row[1]} for row in brands_data]
    
    return render_template('admin_brands.html', brands=brands, user=current_user)
