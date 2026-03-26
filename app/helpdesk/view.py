from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.model.support_repository import SupportRepository
from app.model.user_repository import UserRepository
from app import Utils
import os
import time
from app.auth.view import requires_permission, has_permission
from app.gamification.view import gamification_service
from app.model.journey_repository import JourneyRepository

helpdesk = Blueprint('helpdesk', __name__, url_prefix='/helpdesk')

def validate_banned_user_session():
    """Validate banned user session information"""
    banned_info = session.get('banned_user_info')
    
    if not banned_info:
        return False, "Appeal session has expired. Please login again to start a new appeal.", None
    
    # Check time expiration
    current_time = time.time()
    if current_time > banned_info.get('expires_at', 0):
        session.pop('banned_user_info', None)
        return False, "Appeal session has expired. Please login again to start a new appeal.", None
    
    # Verify user still exists and is still banned
    user = UserRepository.get_user(user_id=banned_info['user_id'])
    if not user or user['status'] != 'banned':
        session.pop('banned_user_info', None)
        return False, "User status has changed. Appeal is no longer valid.", None
    
    return True, None, banned_info

def clear_banned_user_session():
    """Clear banned user session information"""
    session.pop('banned_user_info', None)

@helpdesk.route('/')
@requires_permission('view_request')
def index():
    """Display support requests list"""
    user_id = session['user_id']
    is_staff = session.get('role') in ['admin', 'editor', 'support_tech']
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    issue_type_filter = request.args.get('issue_type')
    
    requests = SupportRepository.get_user_requests(user_id=None if is_staff else user_id, status=status_filter,priority=priority_filter,issue_type=issue_type_filter)
    
    # Create a simple pagination object for testing purposes
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
    
    # Create pagination object
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_requests = len(requests) if requests else 0
    pagination = SimplePagination(total_requests, page, per_page)
    
    # Apply pagination to requests
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_requests = requests[start_index:end_index] if requests else []
    
    return render_template('helpdesk_index.html', 
                           requests=paginated_requests, 
                           is_staff=is_staff,
                           status_filter=status_filter,
                           priority_filter=priority_filter,
                           issue_type_filter=issue_type_filter,
                           pagination=pagination)

@helpdesk.route('/create', methods=['GET', 'POST'])
@requires_permission('create_request')
def create_request():
    """Create a new support request"""
    # Handle journey appeal request
    journey_info = None
    journey_id = request.args.get('journey_id')
    if journey_id:
        journey = JourneyRepository.get_journey(journey_id)
        if journey and journey['user_id'] == session['user_id'] and journey['hidden'] == 1:
            journey_info = journey
        else:
            flash("Invalid journey or you don't have permission to appeal this journey.", "error")
            return redirect(url_for('helpdesk.index'))
    
    # Handle restricted user appeal request
    restricted_user_info = None
    is_restricted_appeal = request.args.get('restricted_appeal') == '1'
    if is_restricted_appeal:
        user = UserRepository.get_user(user_id=session['user_id'])
        if user and user['status'] == 'restricted':
            restricted_user_info = {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email']
            }
        else:
            flash("You are not restricted from sharing. Appeal is not needed.", "info")
            return redirect(url_for('journey.list_journey', page_auth='private'))
    
    if request.method == 'POST':
        issue_type = request.form.get('issue_type')
        summary = request.form.get('summary', '').strip()
        description = request.form.get('description', '').strip()
        screenshot = request.files.get('screenshot')
        form_journey_id = request.form.get('journey_id')
        
        # For journey appeals, validate journey_id and add journey info to description
        if form_journey_id:
            journey = JourneyRepository.get_journey(form_journey_id)
            if journey and journey['user_id'] == session['user_id'] and journey['hidden'] == 1:
                journey_info = journey
            else:
                flash("Invalid journey or you don't have permission to appeal this journey.", "error")
                return render_template('helpdesk_create.html', journey_info=journey_info, restricted_user_info=restricted_user_info)
        
        errors = {}
        if not issue_type:
            errors['issue_type'] = "Please select an issue type"
        if not summary:
            errors['summary'] = "Summary is required"
        elif len(summary) > 50:
            errors['summary'] = "Summary cannot exceed 50 characters"
        if not description:
            errors['description'] = "Description is required"
        elif len(description) > 300:
            errors['description'] = "Description cannot exceed 300 characters"
            
        # Add journey information to description AFTER validation (for journey appeals only)
        if form_journey_id and journey_info:
            journey_details = f"\n\n--- Journey Information ---\nJourney ID: #{journey_info['journey_id']}\nJourney Title: {journey_info['title']}\nCreated: {journey_info['create_time'].strftime('%Y-%m-%d %H:%M:%S')}\nStatus: Hidden\n--- End Journey Information ---"
            description = description + journey_details
        
        # Handle screenshot upload validation
        screenshot_path = None
        if screenshot and screenshot.filename:
            # Check file format first
            if not Utils.allowed_file(screenshot.filename):
                from flask import current_app
                allowed_formats = ', '.join(ext.upper() for ext in current_app.config['ALLOWED_EXTENSIONS'])
                errors['screenshot'] = f"Invalid file format. Please upload an image file with one of these formats: {allowed_formats}"
            else:
                # Check file size
                screenshot.seek(0, os.SEEK_END)
                file_size = screenshot.tell()
                screenshot.seek(0)  # Reset file pointer
                from flask import current_app
                if file_size > current_app.config['MAX_FILE_SIZE']:
                    max_size_mb = current_app.config['MAX_FILE_SIZE'] // (1024 * 1024)
                    errors['screenshot'] = f"File size exceeds the {max_size_mb}MB limit. Please choose a smaller image."
            
        if errors:
            return render_template('helpdesk_create.html', errors=errors, journey_info=journey_info, restricted_user_info=restricted_user_info)
        
        # Handle screenshot upload
        if screenshot and screenshot.filename and Utils.allowed_file(screenshot.filename):
            try:
                from flask import current_app
                upload_folder = os.path.join(current_app.static_folder, 'uploads/support')
                file_ext = screenshot.filename.rsplit('.', 1)[1].lower()
                if journey_info:
                    new_filename = f"journey_appeal_{session['user_id']}_{journey_info['journey_id']}_{int(time.time())}.{file_ext}"
                elif restricted_user_info:
                    new_filename = f"restricted_appeal_{session['user_id']}_{int(time.time())}.{file_ext}"
                else:
                    new_filename = f"support_{session['user_id']}_{int(time.time())}.{file_ext}"
                result = Utils.upload_file(screenshot, upload_folder, new_filename)
                if result:
                    # Convert to relative path for DB storage
                    screenshot_path = result.replace(current_app.static_folder + '/', '')
                else:
                    flash("Failed to upload screenshot. Please try again.", "warning")
            except Exception as e:
                flash(f"Failed to upload screenshot: {e}", "warning")
        
        # Create request
        result = SupportRepository.create_request(
            session['user_id'], 
            issue_type, 
            summary, 
            description, 
            screenshot_path
        )
        
        if result > 0:
            gamification_service.check_achievement(session['user_id'], 7)  # Check for "First Report Submitted" achievement
            gamification_service.check_achievement(session['user_id'], 9)  # Check for "Create at Least 5 Bug/Help/Appeal Request" achievement
            
            if journey_info or restricted_user_info:
                # Show success modal for appeals
                return render_template('helpdesk_create.html', 
                                     show_success_modal=True, 
                                     request_id=result,
                                     journey_info=journey_info,
                                     restricted_user_info=restricted_user_info)
            else:
                flash("Your support request has been submitted successfully.", "success")
                return redirect(url_for('helpdesk.view_request', request_id=result))
        else:
            flash("Failed to submit request. Please try again later.", "danger")
    
    return render_template('helpdesk_create.html', journey_info=journey_info, restricted_user_info=restricted_user_info)

@helpdesk.route('/journey-appeal/<int:journey_id>')
@requires_permission('create_request')
def create_journey_appeal(journey_id):
    """Journey appeal route - redirects to create_request with journey_id"""
    return redirect(url_for('helpdesk.create_request', journey_id=journey_id))

@helpdesk.route('/restricted-appeal')
@requires_permission('create_request')
def create_restricted_appeal():
    """Restricted sharing appeal route - redirects to create_request with restricted_appeal flag"""
    return redirect(url_for('helpdesk.create_request', restricted_appeal='1'))

@helpdesk.route('/view/<int:request_id>')
@requires_permission('view_request')
def view_request(request_id):
    """View support request details"""
    request_details = SupportRepository.get_request_details(request_id)
    
    if not request_details:
        flash("Support request not found.", "danger")
        return redirect(url_for('helpdesk.index'))
    
    # Check permissions - only owner or staff can view
    is_staff = session.get('role') in ['admin', 'editor', 'support_tech']
    is_owner = request_details['user_id'] == session['user_id']
    
    if not is_staff and not is_owner:
        flash("You don't have permission to view this request.", "danger")
        return redirect(url_for('helpdesk.index'))
    
    # Get comments
    comments = SupportRepository.get_request_comments(request_id)
    
    # Get staff users for assignment dropdown
    staff_users = SupportRepository.get_staff_users() if is_staff else []
    
    # Check if user can modify this request
    can_modify = False
    can_comment = False
    
    if is_staff:
        # Staff can only modify if they are the assignee
        can_modify = request_details['assignee_id'] == session['user_id'] if request_details['assignee_id'] else False
        # Staff can comment if they are the owner or assignee
        can_comment = is_owner or (request_details['assignee_id'] == session['user_id'] if request_details['assignee_id'] else False)
    else:
        # Non-staff users can only comment if they are the owner
        can_comment = is_owner
    
    return render_template('helpdesk_view.html', 
                           request=request_details, 
                           comments=comments,
                           is_staff=is_staff,
                           is_owner=is_owner,
                           staff_users=staff_users,
                           can_modify=can_modify,
                           can_comment=can_comment)

@helpdesk.route('/comment/<int:request_id>', methods=['POST'])
@requires_permission('view_request')
def add_comment(request_id):
    """Add comment to support request"""
    comment = request.form.get('comment').strip()
    if not comment:
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for('helpdesk.view_request', request_id=request_id))
    
    request_details = SupportRepository.get_request_details(request_id)
    if not request_details:
        flash("Support request not found.", "danger")
        return redirect(url_for('helpdesk.index'))
    
    # Check permissions - only owner or assigned staff can comment
    is_staff = session.get('role') in ['admin', 'editor', 'support_tech']
    is_owner = request_details['user_id'] == session['user_id']
    is_assignee = request_details['assignee_id'] == session['user_id'] if request_details['assignee_id'] else False
    
    # Only request owner or assigned staff member can comment
    if not is_owner and not is_assignee:
        flash("You don't have permission to comment on this request. Only the request owner or assigned staff member can add comments.", "danger")
        return redirect(url_for('helpdesk.view_request', request_id=request_id))
    
    # Check status - can only comment on non-Resolved requests
    if request_details['status'] == 'Resolved':
        flash("This request is resolved and cannot receive more comments.", "warning")
        return redirect(url_for('helpdesk.view_request', request_id=request_id))
    
    # Add comment
    result = SupportRepository.add_comment(request_id, session['user_id'], comment)
    
    if result > 0:
        gamification_service.check_achievement(session['user_id'], 8)  # Check for "Make Comment on the Bug/Help/Appeal Request" achievement
        flash("Comment added successfully.", "success")
    else:
        flash("Failed to add comment. Please try again later.", "danger")
    
    return redirect(url_for('helpdesk.view_request', request_id=request_id))

@helpdesk.route('/status/<int:request_id>', methods=['POST'])
@requires_permission('view_request')
def update_status(request_id):
    """Update support request status (staff only)"""
    if session.get('role') not in ['admin', 'editor', 'support_tech']:
        flash("You don't have permission to update request status.", "danger")
        return redirect(url_for('helpdesk.index'))
    
    # Get current request details
    request_details = SupportRepository.get_request_details(request_id)
    if not request_details:
        flash("Request not found.", "danger")
        return redirect(url_for('helpdesk.index'))
    
    action = request.form.get('action')
    new_status = request.form.get('status')
    current_status = request_details['status']
    
    # Handle different actions
    if action == 'take' and has_permission('take_request'):
        # Anyone can take an unassigned request
        if request_details['assignee_id'] is not None:
            flash("This request is already assigned to someone else.", "warning")
            return redirect(url_for('helpdesk.view_request', request_id=request_id))
        
        assignee_id = session['user_id']
        # Keep current status unchanged when taking responsibility
        new_status = current_status
            
    elif action == 'drop' and has_permission('drop_request'):
        # Only assigned person can drop the request
        if request_details['assignee_id'] != session['user_id']:
            flash("You can only drop requests assigned to you.", "warning")
            return redirect(url_for('helpdesk.view_request', request_id=request_id))
        
        assignee_id = None
        
    elif action == 'assign':
        # Only allow assignment to unassigned requests
        if request_details['assignee_id'] is not None:
            flash("This request is already assigned. Please drop it first if you want to reassign.", "warning")
            return redirect(url_for('helpdesk.view_request', request_id=request_id))
        
        assignee_id = request.form.get('assignee_id')
        if not assignee_id:
            flash("Please select a staff member to assign.", "warning")
            return redirect(url_for('helpdesk.view_request', request_id=request_id))
        
        assignee_id = int(assignee_id)
        # Keep current status unchanged when assigning
        new_status = current_status
    
    else:
        # For status updates, check if user can modify request (assignee only)
        if not SupportRepository.can_modify_request(request_id, session['user_id']):
            flash("Access denied: Only the assigned staff member can update the status.", "danger")
            return redirect(url_for('helpdesk.view_request', request_id=request_id))
        
        if not new_status:
            flash("Please select a status.", "danger")
            return redirect(url_for('helpdesk.view_request', request_id=request_id))
        
        # Validate status transition - cannot go back to New once opened
        if current_status in ['Open', 'Stalled', 'Resolved'] and new_status == 'New':
            flash("Cannot set status back to 'New' once the request has been opened.", "warning")
            return redirect(url_for('helpdesk.view_request', request_id=request_id))
        
        # Keep current assignee
        assignee_id = request_details.get('assignee_id')
    
    # Update status
    result = SupportRepository.update_request_status(request_id, new_status, assignee_id)
    
    if result:
        if action == 'take':
            flash("You've successfully taken responsibility for this request.", "success")
        elif action == 'drop':
            flash("You've successfully unassigned yourself from this request.", "success")
        elif action == 'assign':
            flash("Request has been successfully assigned.", "success")
        else:
            flash("Request status updated successfully.", "success")
    else:
        flash("Failed to update request status. Please try again later.", "danger")
    
    return redirect(url_for('helpdesk.view_request', request_id=request_id))

@helpdesk.route('/ban-appeal', methods=['GET', 'POST'])
def create_ban_appeal():
    """Create ban appeal for banned users without login requirement"""
    # Validate banned user session
    is_valid, error_msg, banned_info = validate_banned_user_session()
    
    if not is_valid:
        flash(error_msg, "error")
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        summary = request.form.get('summary', '').strip()
        description = request.form.get('description', '').strip()
        screenshot = request.files.get('screenshot')
        
        # Validation
        errors = {}
        if not summary:
            errors['summary'] = "Appeal summary is required"
        elif len(summary) > 50:
            errors['summary'] = "Summary cannot exceed 50 characters"
            
        if not description:
            errors['description'] = "Detailed explanation is required"
        elif len(description) > 300:
            errors['description'] = "Description cannot exceed 300 characters"
            
        # Handle screenshot upload validation
        screenshot_path = None
        if screenshot and screenshot.filename:
            # Check file format first
            if not Utils.allowed_file(screenshot.filename):
                from flask import current_app
                allowed_formats = ', '.join(ext.upper() for ext in current_app.config['ALLOWED_EXTENSIONS'])
                errors['screenshot'] = f"Invalid file format. Please upload an image file with one of these formats: {allowed_formats}"
            else:
                # Check file size
                screenshot.seek(0, os.SEEK_END)
                file_size = screenshot.tell()
                screenshot.seek(0)  # Reset file pointer
                from flask import current_app
                if file_size > current_app.config['MAX_FILE_SIZE']:
                    max_size_mb = current_app.config['MAX_FILE_SIZE'] // (1024 * 1024)
                    errors['screenshot'] = f"File size exceeds the {max_size_mb}MB limit. Please choose a smaller image."
            
        if errors:
            return render_template('helpdesk_create.html', 
                                 errors=errors, 
                                 banned_user_info=banned_info)
        
        # Handle screenshot upload
        if screenshot and screenshot.filename and Utils.allowed_file(screenshot.filename):
            try:
                from flask import current_app
                upload_folder = os.path.join(current_app.static_folder, 'uploads/support')
                file_ext = screenshot.filename.rsplit('.', 1)[1].lower()
                new_filename = f"ban_appeal_{banned_info['user_id']}_{int(time.time())}.{file_ext}"
                result = Utils.upload_file(screenshot, upload_folder, new_filename)
                if result:
                    # Convert to relative path for DB storage
                    screenshot_path = result.replace(current_app.static_folder + '/', '')
                else:
                    flash("Failed to upload screenshot. Please try again.", "warning")
                    return render_template('helpdesk_create.html', banned_user_info=banned_info)
            except Exception as e:
                flash(f"Failed to upload screenshot: {e}", "warning")
                return render_template('helpdesk_create.html', banned_user_info=banned_info)
        
        # Create ban appeal request
        result = SupportRepository.create_request(
            banned_info['user_id'], 
            'Appeal', 
            summary, 
            description, 
            screenshot_path
        )
        
        if result > 0:
            # Clear session to prevent multiple submissions
            clear_banned_user_session()
            
            # Show success modal
            return render_template('helpdesk_create.html', 
                                 show_success_modal=True, 
                                 request_id=result,
                                 banned_user_info=None)
        else:
            flash("Failed to submit ban appeal. Please try again later.", "danger")
            return render_template('helpdesk_create.html', banned_user_info=banned_info)
    
    # GET request - show the form
    return render_template('helpdesk_create.html', banned_user_info=banned_info)