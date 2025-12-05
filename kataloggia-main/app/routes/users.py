"""
Public user routes - Browse and view user profiles
"""
from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from models import User, Collection

bp = Blueprint('users', __name__)

@bp.route('/users')
@login_required
def list_users():
    """Kullanıcı listesi sayfası"""
    from app.repositories import get_repository
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Search query
    search_query = request.args.get('q', '').strip()
    
    # Get users from repository
    repo = get_repository()
    all_users_data = repo.get_all_users(limit=per_page, offset=offset)
    
    # Convert to User objects and filter by search if needed
    users = []
    for user_data in all_users_data:
        user = User.get_by_id(user_data.get('id'))
        if user:
            # Filter by search query if provided
            if search_query:
                if search_query.lower() in user.username.lower() or search_query.lower() in user.email.lower():
                    users.append(user)
            else:
                users.append(user)
    
    # If search query, filter all users (not just current page)
    if search_query and not users:
        # Get more users for search
        all_users_data = repo.get_all_users(limit=500, offset=0)
        for user_data in all_users_data:
            user = User.get_by_id(user_data.get('id'))
            if user and (search_query.lower() in user.username.lower() or search_query.lower() in user.email.lower()):
                users.append(user)
    
    return render_template('users_list.html', 
                         users=users, 
                         current_user=current_user,
                         search_query=search_query,
                         page=page)

@bp.route('/user/<username>')
@login_required
def public_profile(username):
    """Public kullanıcı profili"""
    user = User.get_by_username(username)
    
    if not user:
        abort(404)
    
    # Get user's public collections
    collections = user.get_collections()
    public_collections = [c for c in collections if c.is_public]
    
    # Calculate stats
    total_products = len(user.get_products())
    
    # Check if current user is following this user
    is_following = False
    followers_count = 0
    following_count = 0
    if current_user.is_authenticated:
        from app.repositories import get_repository
        repo = get_repository()
        if current_user.id != user.id:
            is_following = repo.is_following(current_user.id, user.id)
        
        # Get follower and following counts
        followers = repo.get_followers(user.id)
        following = repo.get_following(user.id)
        followers_count = len(followers)
        following_count = len(following)
    
    # Format created_at for template
    user_created_at_str = 'N/A'
    if user.created_at:
        try:
            if hasattr(user.created_at, 'strftime'):
                user_created_at_str = user.created_at.strftime('%d.%m.%Y')
            elif isinstance(user.created_at, str):
                user_created_at_str = user.created_at[:10]
        except:
            user_created_at_str = 'N/A'
    
    # Format collection created_at dates and get like info
    from app.repositories import get_repository
    repo = get_repository()
    for collection in public_collections:
        if collection.created_at:
            try:
                if hasattr(collection.created_at, 'strftime'):
                    collection.created_at_str = collection.created_at.strftime('%d.%m.%Y')
                elif isinstance(collection.created_at, str):
                    collection.created_at_str = collection.created_at[:10]
                else:
                    collection.created_at_str = 'N/A'
            except:
                collection.created_at_str = 'N/A'
        else:
            collection.created_at_str = 'N/A'
        
        # Get like status and count for each collection
        if current_user.is_authenticated:
            collection.is_liked = repo.is_collection_liked(current_user.id, collection.id)
        else:
            collection.is_liked = False
        collection.likes_count = repo.get_collection_likes_count(collection.id)
    
    return render_template('public_profile.html',
                         user=user,
                         collections=public_collections,
                         total_products=total_products,
                         user_created_at_str=user_created_at_str,
                         is_following=is_following,
                         is_own_profile=(current_user.is_authenticated and current_user.id == user.id),
                         followers_count=followers_count,
                         following_count=following_count)

