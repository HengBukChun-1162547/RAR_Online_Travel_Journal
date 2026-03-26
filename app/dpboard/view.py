from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.auth.view import requires_permission
from app.model.departure_board_repository import DepartureRepository
from app import db
from functools import wraps
from flask import redirect, url_for, flash, session
from app.model.user_repository import UserRepository

class SimplePagination:
    def __init__(self, total_items, page=1, per_page=10):
        self.page = page
        self.per_page = per_page
        self.total = total_items
        self.pages = max(1, (total_items + per_page - 1) // per_page)
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None
    
    def iter_pages(self):
        # Simple pagination: show current page and surrounding pages
        for i in range(max(1, self.page - 2), min(self.pages + 1, self.page + 3)):
            yield i

def check_departure_board_access():
    """
    Decorator for checking departure board access.
    Verifies if user has permission or active subscription.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('auth.login'))
            
            # Check if user is staff (who always have access)
            is_staff = session.get('role') in ['editor', 'admin', 'support_tech']
            
            # Check if user has active subscription
            has_active_subscription = False
            if not is_staff:
                subscription = UserRepository.get_active_subscription(user_id)
                has_active_subscription = subscription is not None
            
            # If not staff and no active subscription
            if not is_staff and not has_active_subscription:
                flash('Your subscription has expired. Please renew to access the Departure Board.', 'warning')
                return redirect(url_for('premium.subscribe_to_premium_features'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

departure_board = Blueprint('departure_board', __name__, url_prefix='/departure_board')

@departure_board.route('/')
@check_departure_board_access()
def index():
    user_id = session.get('user_id')
    filter_type = request.args.get('filter')
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Get events for the departure board with pagination
    result = DepartureRepository.get_departure_board_events(user_id, filter_type, page, per_page)
    
    # Create SimplePagination object for template
    pagination = SimplePagination(result['pagination']['total'], page, per_page)
    
    return render_template('departure_board.html',
                          events=result['events'],
                          followed_journeys=result['followed_journeys'],
                          followed_users=result['followed_users'],
                          followed_locations=result['followed_locations'],
                          filter_type=filter_type,
                          pagination=pagination)

@departure_board.route('/unfollow/<follow_type>/<int:follow_id>', methods=['POST'])
@check_departure_board_access()
def unfollow(follow_type, follow_id):
    user_id = session.get('user_id')
    result = False
    
    if follow_type == 'journey':
        result = DepartureRepository.unfollow_journey(user_id, follow_id)
    elif follow_type == 'user':
        result = DepartureRepository.unfollow_user(user_id, follow_id)
    elif follow_type == 'location':
        result = DepartureRepository.unfollow_location(user_id, follow_id)
    
    if result:
        flash(f'Successfully unfollowed {follow_type}', 'success')
    else:
        flash(f'Error unfollowing {follow_type}', 'danger')
        
    # Redirect back to the same page with the same filter and pagination
    page = request.args.get('page', 1)
    filter_type = request.args.get('filter')
    
    redirect_url = url_for('departure_board.index')
    if filter_type:
        redirect_url += f'?filter={filter_type}'
        if page and page != '1':
            redirect_url += f'&page={page}'
    elif page and page != '1':
        redirect_url += f'?page={page}'
        
    return redirect(redirect_url)