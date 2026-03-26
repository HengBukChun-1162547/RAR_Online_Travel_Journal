from flask import Blueprint, render_template, session, redirect, url_for, request, flash, g, current_app
from app import flask_bcrypt
from functools import wraps
from app.model import *
import time

auth = Blueprint('auth', __name__)

"""
    A decorator that checks if the user is logged in 
    and has the required permission to access a function.
"""


def requires_permission(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if 'loggedin' not in session:
                flash("You need to be logged in to access this page.", "error")
                return redirect(url_for('auth.login'))
            # Check if user has the required permission
            if not has_permission(permission_name):
                flash(
                    "Sorry, you don't have the required permissions to view this page.", "error")
                return render_template('access_denied.html'), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def has_permission(permission_name, user_id=None):
    """Check if the user has a specific permission."""
    if user_id is None:
        user_permissions = session.get('permissions', [])
    else:
        user_permissions = AuthorityRepository.get_user_permissions(user_id)
    return permission_name in user_permissions


def update_session(user_id):
    """Update the session with user details."""
    if user_id:
        user = UserRepository.get_user(user_id)
        session['loggedin'] = True
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['status'] = user['status']

        permissions = AuthorityRepository.get_user_permissions(user['user_id'])
        session['permissions'] = permissions if permissions is not None else []
        if permissions is None:
            flash("Error retrieving user permissions.", "error")
        
        achievements = GamificationRepository.get_user_achievement(user['user_id'])
        session['achievements'] = achievements if achievements is not None else []
        if achievements is None:
            flash("Error retrieving user achievements.", "error")


"""
A function that checks if a user is loggedin and gets the role of the user if it exists and assigns
default None if role does not exist. Based on the user role the function redirects to the corresponding url endpoint.
If the user is not loggedin, they are redirected to the loggin endpoint. 
"""


def user_home_url():
    if 'loggedin' in session:
        return url_for('auth.landing')
    else:
        return url_for('auth.home')


""" redirects users to the user_home_url """


@auth.route('/')
def root():
    return redirect(user_home_url())


""" renders a landing homepage for all users that are not logged"""


@auth.route('/home')
def home():
    if 'loggedin' in session:
        return redirect(user_home_url())
    
    journeys = JourneyRepository.get_journeys(
        role=None,
        user_id=None,
        page_auth='published',
        show_hidden='0',  # exclude hidden journeys
    )

    # Limit number of journeys if needed
    # featured_journeys = journeys[:1]

    return render_template('home.html', journeys=journeys)


@auth.route('/published_events')
def published_events():
    """List all events in a specific journey"""
    # Identify the journey
    journey_id = request.args.get('journey_id')
    # Show all the event items in selected journey
    journey = JourneyRepository.get_journey(journey_id)

    # Error handling when journey does not exist
    if not journey:
        flash('Journey does not exist.', 'error')
        return redirect(user_home_url())

    if journey['status'] != 'published' or journey['hidden'] == '1':
        flash('This journey is not published', 'error')
        return redirect(user_home_url())

    events = EventRepository.get_event_list_details(journey_id)
    can_create = False
    can_view = False
    can_edit = False
    staff_can_edit = False
    can_delete_cover = False
    can_upload_cover = False
    session['page_auth'] = 'published'
    return render_template('journey_detail.html',
                           journey=journey,
                           events=events,
                           user=None,
                           can_create=can_create,
                           can_view=can_view,
                           can_edit=can_edit,
                           staff_can_edit=staff_can_edit,
                           can_delete_cover=can_delete_cover,
                           can_upload_cover=can_upload_cover)

@auth.route('/published_events/detail/<int:event_id>')
def published_event_detail(event_id):
    """Display detailed view of an event"""
    # Get event details
    event = EventRepository.get_event_locaiton_details(event_id)
    event_images = EventRepository.get_event_images(event_id)
    page_auth = 'published'

    if not event:
        flash('Event does not exist.', 'error')
        return redirect(user_home_url())

    if event['status'] != 'published' or event['hidden'] == '1':
        flash('This journey is not published', 'error')
        return redirect(user_home_url())
    
    can_view_multiple_photos = False
    user = UserRepository.get_user(event['user_id'])
    if has_permission('add_multiple_photos', event['user_id']):
        can_view_multiple_photos = True

    return render_template(
        'event_detail.html',
        event=event,
        event_images=event_images,
        can_edit=False,
        is_owner=False,
        is_staff=False,
        can_view_multiple_photos=can_view_multiple_photos
    )


""" renders the landing page for logged in users with dashboard data """


@auth.route('/landing')
@requires_permission('view_landing_page')
def landing():
    # Get some useful statistics for the current user
    # Initialize an empty dictionary for stats
    stats = {}

    # Count unread announcements
    result = AnnouncementRepository.get_unread_announcements_count(
        session['user_id'])
    stats['unread_announcements'] = result if result else 0

    # Render the main page with sidebar
    return render_template('landing.html', **stats)


""" Login page for users. If the user is already logged in, they are redirected to their home page."""


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(user_home_url())

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        session.permanent = True
        username = request.form['username']
        password = request.form['password']
        
        # Attempt to validate the login details against the database.
        account = UserRepository.get_user(username=username)
        # Redirect banned accounts to access denied page
        if (account is not None and account['status'] == 'banned'):
            # Store banned user info temporarily for appeal process (3 minutes expiry)
            session['banned_user_info'] = {
                'user_id': account['user_id'],
                'username': account['username'],
                'email': account['email'],
                'created_at': time.time(),
                'expires_at': time.time() + 600
            }
            return render_template('access_denied.html', user_status=account['status'])

        if account is not None:
            password_hash = account['password_hash']

            if flask_bcrypt.check_password_hash(password_hash, password):
                update_session(account['user_id'])
                from app.gamification.view import gamification_service
                gamification_service.check_achievement(account['user_id'], 5)  # Check for "Longest Journey" achievement
                return redirect(user_home_url())
            else:
                return render_template('login.html',
                                       username=username,
                                       password_invalid=True)
        else:
            return render_template('login.html',
                                   username=username,
                                   username_invalid=True)
    return render_template('login.html')


""" Method logs out user and redirects them to login page"""


@auth.route('/logout')
def logout():
    # removes session data when logged out
    session.clear()
    return redirect(url_for('auth.home'))
