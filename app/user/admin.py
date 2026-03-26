from app.user import user
from app.auth.view import requires_permission
from flask import redirect, render_template, request, session, url_for, flash, current_app, jsonify
from app.model import *
from app import Pagination
import json

### Read and display the details of all users with SQL query
@user.route('/users', methods=['GET','POST'])
@requires_permission('view_user_management')
def users():
    """
    - To show the list with their role and status in ascending order by referring username.
    - If the user is not logged in, they are redirected to the login page.
    - Displays an individual user profile if a specific user_id is requested.
    - Allows admin user to update all roles and statuses via form submission. 
    """
     
    # Get search query from URL parameters
    search_query = request.args.get('q', '').strip()
    
    # Fetch users' detail from the database with SQL query (with or without search)
    if search_query:
        search_pattern = f"%{search_query}%"
        all_users = UserRepository.get_user(search_user=search_pattern)
        if not all_users:
            flash(f"No results found for '{search_query}'", "info")
            all_users = []
    else:
        all_users = UserRepository.get_user()

    # Handle get request and post request for updating specific user role or status 
    user_id = request.form.get('user_id') or request.args.get('user_id')
    new_role = request.form.get('role') or request.args.get('role')
    new_status = request.form.get('status') or request.args.get('status')
    # Get the page from which the user is redirected
    page = request.values.get('page')

    # Update user status in database with SQL query if selected user's new status is updated   
    if new_status:
        UserRepository.update_user(user_id, status=new_status)
        flash(f"The user's status has been successfully updated to '{new_status.capitalize()}'.", "success")  # Notify user
        redirect_params = {'page': page, 'user_id': user_id}
        if search_query:
            redirect_params['q'] = search_query
        filter_param = request.form.get('filter') or request.args.get('filter')
        if filter_param:
            redirect_params['filter'] = filter_param
        return redirect(url_for('user.users', **redirect_params))
          
    # Update user role in database with SQL query if selected user's new status is updated     
    if new_role:
        UserRepository.update_user(user_id, role=new_role)
        flash(f"The user's role has been successfully updated to '{new_role.capitalize()}'.", "success")  # Notify user
        redirect_params = {'page': page, 'user_id': user_id}
        if search_query:
            redirect_params['q'] = search_query
        filter_param = request.form.get('filter') or request.args.get('filter')
        if filter_param:
            redirect_params['filter'] = filter_param
        return redirect(url_for('user.users', **redirect_params))
     
    # Show the specific user's profile if user is selected with SQL query
    if page == 'profile':
        selected_user_id = request.args.get('user_id')      
        if selected_user_id:
            profile = UserRepository.get_user(user_id=selected_user_id)
            active_subscription = UserRepository.get_active_subscription(selected_user_id)
                
            return render_template('profile.html', 
                              profile=profile, 
                              selected_user_id=selected_user_id,
                              active_subscription=active_subscription,
                              is_staff=True) # Render the profile template

    # Apply filtering feature based on the selected option
    filtered_users = all_users
    filter_type = request.form.get('filter') or request.args.get('filter')

    # Use for looping and if statement to filter and update the comment list based on certain requirements
    if filter_type:        
        if filter_type == 'Editor':
            filtered_users = [u for u in all_users if u['role'] == 'editor']
        elif filter_type == 'Admin':
            filtered_users = [u for u in all_users if u['role'] == 'admin']
        elif filter_type == 'Support_tech':
            filtered_users = [u for u in all_users if u['role'] == 'support_tech']
        elif filter_type == 'Traveller':
            filtered_users = [u for u in all_users if u['role'] == 'traveller']
        elif filter_type == 'Trial':
            filtered_users = [u for u in all_users if u['role'] == 'trial']
        elif filter_type == 'Premium':
            filtered_users = [u for u in all_users if u['role'] == 'premium']
        elif filter_type == 'Staffs':
            filtered_users = [u for u in all_users if u['role'] != 'traveller' and u['role'] != 'trial' and u['role'] != 'premium']
        elif filter_type == 'Block':
            filtered_users = [u for u in all_users if u['status'] == 'restricted']
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_users = len(filtered_users) if filtered_users else 0
    
    # Apply pagination to the users list
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_users = filtered_users[start_index:end_index] if filtered_users else []
    
    # Create pagination object using standard Pagination class
    pagination = Pagination(page, per_page, total_users)
    
    # Pass pagination object to template
    return render_template('users.html', 
                           users=paginated_users, 
                           all_users=all_users, 
                           filter_type=filter_type,
                           pagination=pagination) # Render the user list template


# In admin.py

@user.route('/user/<int:user_id>', methods=['GET'])
@requires_permission('view_others_profile')
def user_view(user_id):
    """
    - Displays an individual user's profile.
    - Only accessible by the admin.
    """
    if session['role'] != 'admin':
        return render_template('access_denied.html'), 403  # Only admin can view this page

    # Fetch user details by user_id
    user_details = UserRepository.get_user(user_id=user_id)

    if user_details:
        return render_template('user_view.html', user=user_details)  # Render profile template
    else:
        flash(f'User with ID {user_id} not found', 'danger')
        return redirect(url_for('admin.users'))  # Redirect if user not found



@user.route('/inform', methods=['GET'])
@requires_permission('view_announcements')
def inform():
    """
    Display a combined page for announcements and subscription notifications with tabs.
    - If the user is not logged in, they are redirected to the login page.
    - Shows announcements and subscription messages in separate tabs.
    - Each tab has its own pagination system.
    """
    # Get active tab from URL parameters (default to 'announcements')
    active_tab = request.args.get('tab', 'announcements')
    # Get pagination parameters for announcements
    announcements_page = request.args.get('announcements_page', 1, type=int)

    # Get pagination parameters for subscription messages
    subscriptions_page = request.args.get('subscriptions_page', 1, type=int)

    # Get pagination parameters from edit log messages
    edit_log_page = request.args.get('edit_logs_page', 1, type=int)

    # Items per page from config
    announcement_per_page = current_app.config['ANNOUNCEMENT_PAGE_LIMIT']

    # Get announcements data
    announcements_list = AnnouncementRepository.get_announcement()
    announcements_total_items = len(announcements_list)
    announcements_total_pages = (announcements_total_items + announcement_per_page - 1) // announcement_per_page
    announcements_offset = (announcements_page - 1) * announcement_per_page
    announcements_list = announcements_list[announcements_offset:announcements_offset+announcement_per_page]

    # Get subscription messages data
    subscription_messages = []
    if 'user_id' in session:
        subscription_messages = NotificationRepository.get_system_notification_details(session['user_id'])

    # Items per page from config
    subscriptions_per_page = current_app.config['SUBSCRIPTION_PAGE_LIMIT']

    subscriptions_total_items = len(subscription_messages)
    subscriptions_total_pages = (subscriptions_total_items + subscriptions_per_page - 1) // subscriptions_per_page
    subscriptions_offset = (subscriptions_page - 1) * subscriptions_per_page
    subscription_messages = subscription_messages[subscriptions_offset:subscriptions_offset+subscriptions_per_page]

    # Get edit log messages data
    edit_log_messages = []
    if 'user_id' in session:
        edit_log_messages = EditLogRepository.get_edit_logs_by_journey_user(session['user_id'])
        for edit_log in edit_log_messages:
            edit_log['summary'] = json.loads(edit_log['summary']) if edit_log['summary'] else None
    
    # Items per page from config
    edit_log_per_page = current_app.config['EDIT_LOG_PAGE_LIMIT']
    edit_log_total_items = len(edit_log_messages)
    edit_log_total_pages = (edit_log_total_items + edit_log_per_page - 1) // edit_log_per_page
    edit_log_offset = (edit_log_page - 1) * edit_log_per_page
    edit_log_messages = edit_log_messages[edit_log_offset:edit_log_offset+edit_log_per_page]

    # Get unread announcements and counts
    unread_announcements = []
    announcements_unread_count = 0
    if 'user_id' in session:
        unread_announcements = AnnouncementRepository.get_unread_announcement_ids(session['user_id'])
        announcements_unread_count = AnnouncementRepository.get_unread_announcements_count(session['user_id'])

    # Get unread subscription notifications and counts
    unread_subscriptions = []
    subscriptions_unread_count = 0
    if 'user_id' in session:
        unread_subscriptions_dict = NotificationRepository.get_unread_system_notification_ids(session['user_id'])
        unread_subscriptions = [notification['notification_id'] for notification in unread_subscriptions_dict]
        subscriptions_unread_count = len(unread_subscriptions)

    # Get unread edit log messages and counts
    unread_edit_logs = []
    edit_logs_unread_count = 0
    if 'user_id' in session:
        unread_edit_logs = EditNotificationRepository.get_unread_notifications(session['user_id'])
        unread_edit_log_ids = [log['edit_log_id'] for log in unread_edit_logs]
        edit_logs_unread_count = len(unread_edit_logs)

    return render_template(
        'inform.html',  # Using the inform.html template
        # Announcements data
        announcements=announcements_list,
        unread_announcements=unread_announcements,
        announcements_unread_count=announcements_unread_count,
        announcements_current_page=announcements_page,
        announcements_total_pages=announcements_total_pages,
        announcements_total_items=announcements_total_items,
        
        # Subscription messages data
        subscription_messages=subscription_messages,
        unread_subscriptions=unread_subscriptions,
        subscriptions_unread_count=subscriptions_unread_count,
        subscriptions_current_page=subscriptions_page,
        subscriptions_total_pages=subscriptions_total_pages,
        subscriptions_total_items=subscriptions_total_items,
        
        # Edit log messages data
        edit_logs=edit_log_messages,
        unread_edit_log_ids=unread_edit_log_ids,
        edit_logs_unread_count=edit_logs_unread_count,
        edit_logs_current_page=edit_log_page,
        edit_logs_total_pages=edit_log_total_pages,
        edit_logs_total_items=edit_log_total_items,

        # Active tab
        active_tab=active_tab)

@user.route('/announcement/<int:announcement_id>', methods=['GET'])
@requires_permission('view_announcements')
def announcement_detail(announcement_id):
    """
    Display a specific announcement's details.
    - If the user is not logged in, they are redirected to the login page.
    - Marks the announcement as read for the current user.
    """
    # Get the announcement details
    announcement = AnnouncementRepository.get_announcement(announcement_id=announcement_id)
    
    if not announcement:
        flash("Announcement not found.", "danger")
        return redirect(url_for('user.inform'))
    
    # Mark announcement as read for current user
    if 'user_id' in session:
        AnnouncementRepository.mark_announcement_as_read(session['user_id'], announcement_id)
    
    return render_template('announcement_detail.html', announcement=announcement)

@user.route('/announcement/create', methods=['GET', 'POST'])
@requires_permission('create_announcements')
def create_announcement():
    """
    Create a new announcement.
    - Only users with admin or editor roles can create announcements.
    - Redirects to the announcement list after creation.
    """
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Validate form data
        if not title or not description:
            flash("Title and description are required.", "danger")
            return render_template('announcement_form.html', action="create")
        
        # Create the announcement
        result = AnnouncementRepository.create_announcement(session['user_id'], title, description)
        
        if result > 0:
            flash("Announcement created successfully.", "success")
            return redirect(url_for('user.inform'))
        else:
            flash("Failed to create announcement.", "danger")
    
    return render_template('announcement_form.html', action="create")

@user.route('/announcement/edit/<int:announcement_id>', methods=['GET', 'POST'])
@requires_permission('edit_announcements')
def edit_announcement(announcement_id):
    """
    Edit an existing announcement.
    - Only the creator or users with admin role can edit the announcement.
    - Redirects to the announcement detail page after editing.
    """
    # Get the announcement
    announcement = AnnouncementRepository.get_announcement(announcement_id=announcement_id)
    
    if not announcement:
        flash("Announcement not found.", "danger")
        return redirect(url_for('user.inform'))
    
    # Check if the user has permission to edit
    if announcement['user_id'] != session['user_id'] and session.get('role') != 'admin':
        flash("You do not have permission to edit this announcement.", "danger")
        return redirect(url_for('user.announcement_detail', announcement_id=announcement_id))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Validate form data
        if not title or not description:
            flash("Title and description are required.", "danger")
            return render_template('announcement_form.html', action="edit", announcement=announcement)
        
        # Update the announcement
        result = AnnouncementRepository.update_announcement(
            announcement_id=announcement_id,
            update_by=session['user_id'],
            title=title,
            description=description
        )
        
        if result:
            flash("Announcement updated successfully.", "success")
            return redirect(url_for('user.announcement_detail', announcement_id=announcement_id))
        else:
            flash("Failed to update announcement.", "danger")
    
    return render_template('announcement_form.html', action="edit", announcement=announcement)

@user.route('/announcement/delete/<int:announcement_id>', methods=['POST'])
@requires_permission('delete_announcements')
def delete_announcement(announcement_id):
    """
    Delete an announcement.
    - Only the creator or users with admin role can delete the announcement.
    - Redirects to the announcement list after deletion.
    """
    # Get the announcement
    announcement = AnnouncementRepository.get_announcement(announcement_id=announcement_id)
    
    if not announcement:
        flash("Announcement not found.", "danger")
        return redirect(url_for('user.inform'))
    
    # Check if the user has permission to delete
    if announcement['user_id'] != session['user_id'] and session.get('role') != 'admin':
        flash("You do not have permission to delete this announcement.", "danger")
        return redirect(url_for('user.announcement_detail', announcement_id=announcement_id))
    
    # Delete the announcement
    result = AnnouncementRepository.delete_announcement(announcement_id)
    
    if result:
        flash("Announcement deleted successfully.", "success")
    else:
        flash("Failed to delete announcement.", "danger")
    
    return redirect(url_for('user.inform'))