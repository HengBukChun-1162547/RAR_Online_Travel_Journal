from flask import render_template, flash, request, session, redirect, url_for, current_app
from flask import Blueprint
from datetime import date
from app.model import *
from app.gamification.view import gamification_service
from app.auth.view import requires_permission, has_permission
from werkzeug.utils import secure_filename
from app import Utils, Pagination
import uuid
import os
import json

journey = Blueprint('journey', __name__)

""" A method that displays the journeys and events. It allows for journeys to be searched either by title, description or both,
On clearing the search it displays a complete list of the public journeys."""
@journey.route('/journey', methods = ['GET', 'POST'])
@requires_permission('view_own_journey')
def list_journey():
    user_id = session['user_id']
    role = session['role']
    show_hidden = request.values.get('show_hidden', '0')
    page_auth = request.values.get('page_auth')
    searchjourneycontext = ''
    searchjourneyby = ''

    if page_auth == None or (not has_permission('view_hidden_journey') and show_hidden == '1'):
        return render_template('access_denied.html'), 403

    session['page_auth'] = page_auth


    # Get the list of events from the database
    events = EventRepository.get_events()
    # Get the user details from the database
    user = UserRepository.get_user(user_id=user_id)
    view_hidden_journey = has_permission('view_hidden_journey')
    # For handling search requests (both POST and GET with search parameters)
    if request.method == 'POST':
        searchjourneycontext = request.form.get('searchjourneycontext', '').strip()
        searchjourneyby = request.form.get('searchjourneyby').strip()
    else:
        # Handle GET requests with search parameters (from pagination links)
        searchjourneycontext = request.args.get('searchjourneycontext', '').strip()
        searchjourneyby = request.args.get('searchjourneyby', '').strip()
    
    # Handle search processing
    if searchjourneyby and searchjourneycontext:
        search_input = []
        if searchjourneyby == '4':
            search_input = [event["journey_id"] for event in events if searchjourneycontext.lower() in event["name"].lower()]
        elif searchjourneyby in('1', '2', '3', '5'):
            search_input.append(searchjourneycontext)
        journeys = JourneyRepository.get_journeys(role, user_id, page_auth, None, show_hidden, view_hidden_journey, searchjourneyby, search_input)
    else:
        # Get the list of journeys from the database without search
        journeys = JourneyRepository.get_journeys(role, user_id, page_auth, None, show_hidden, view_hidden_journey)

    # Create pagination object
    page = request.values.get('page', 1, type=int)
    per_page = current_app.config['JOURNEY_PAGE_LIMIT'] # number of items per page
    total_items = len(journeys)
    offset = (page - 1) * per_page
    journeys_page = journeys[offset:offset+per_page]
    pagination = Pagination(page, per_page, total_items)

    return render_template('journey_list.html',
                         page_auth=page_auth,
                         journeys=journeys_page,
                         events=events,
                         user=user,
                         show_hidden=show_hidden,
                         pagination=pagination,
                         searchjourneyby=searchjourneyby,
                         searchjourneycontext=searchjourneycontext)


""" A method that displays the add journey form,
    the data is validated and if valid, the journey is added to the database.
"""
@journey.route('/journey/add', methods=['GET', 'POST'])
@requires_permission('create_own_journey')
def add_journey():
    user_id = session['user_id']
    mini_length = 5
    max_length = 50  # title max length
    description_max_length = 300  # description max length
    title_invalid = False
    description_invalid = False
    user = UserRepository.get_user(user_id=user_id)
    if request.method=='POST' and 'title' in request.form and 'description' in request.form and 'sharing' in request.form:
        # Get the details submitted by the user from the session
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        sharing = request.form['sharing']

        # validate the data
        if len(title) < mini_length or len(title) > max_length:
            title_invalid = True
        if len(description) < mini_length or len(description) > description_max_length:
            description_invalid = True
        if title_invalid or description_invalid:
            journey = {'title': title, 'description': description, 'start_date': start_date, 'status': sharing}
            return render_template('journey_form.html', journey=journey, user=user, mode='add', title_invalid=title_invalid, description_invalid = description_invalid)

        # Add the journey to the database
        result = JourneyRepository.add_journey(user_id, title, description, start_date, sharing)
        # return messages and redirect to page
        if result:
            gamification_service.check_achievement(user_id, 1)  # Check for "Creating the First Journey" achievement
            if sharing == 'public':
                gamification_service.check_achievement(user_id, 3)  # Check for "Creating the Journey as Public" achievement 
            if sharing == 'published':
                gamification_service.check_achievement(user_id, 14)  # Check for "First Journey a User Publishes on the Homepage" achievement
            flash('Journey added successfully', 'success')
        else:
            flash('Failed to add journey', 'error')
        return redirect(url_for('journey.list_journey', page_auth='private'))

    today = date.today()
    mode = 'add'
    # GET request or invalid POST, render form
    return render_template('journey_form.html', user=user, today=today, mode=mode)


""" A method that displays the edit journey form.
    The user can only edit their own journeys or if they are an admin or editor.
"""
@journey.route('/journey/edit/<int:journey_id>', methods=['GET', 'POST'])
@requires_permission('edit_own_journey')
def edit_journey(journey_id):
    user_id = session['user_id']
    role = session['role']
    journey = JourneyRepository.get_journeys(role, user_id, '', journey_id)

    # Check if journey exists
    if not journey:
        flash('Journey not found', 'error')
        return redirect(url_for('journey.list_journey', page_auth='private'))

    # Check if the user is allowed to edit this journey
    is_owner = user_id == journey['user_id']
    is_staff = role in ['admin', 'editor', 'support_tech']

    # If the journey has no_edits flag enabled and the user is not the owner, deny access
    if journey['no_edits'] == 1 and not is_owner:
        flash('This journey is protected from editing by its owner', 'error')
        return render_template('access_denied.html'), 403

    # If the user is not the owner and doesn't have permission to edit others' journeys, deny access
    if not is_owner:
        if journey['status'] == 'private' and not has_permission('edit_others_private_journey'):
            return render_template('access_denied.html'), 403
        elif journey['status'] == 'public' and not has_permission('edit_others_puclic_journey'):
            return render_template('access_denied.html'), 403
        elif journey['status'] == 'published' and not has_permission('edit_others_published_journey'):
            return render_template('access_denied.html'), 403

    if request.method=='POST' and 'title' in request.form and 'description' in request.form:
        # Get the details submitted by the user and user_id from the session
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        if 'sharing' in request.form:
            sharing = request.form['sharing']
        else:
            sharing = None
        if 'staff_reason' in request.form:
            edit_reason = request.form['staff_reason']
            summary = []
        else:
            edit_reason = None
        page_auth = request.form['page_auth']
        show_hidden = request.form.get('show_hidden', '0')

        # default parameters for the edit log
        no_edits = None
        result_update_edit_log = None

        # Handle no_edits flag (only for journey owner with create_no_edits_flag and view_own_no_edits_flag permissions)
        if is_owner and has_permission('create_no_edits_flag') and has_permission('view_own_no_edits_flag'):
            no_edits = '1' if 'no_edits' in request.form else '0'
            # Only update no_edits if the journey is public or published
            if journey['status'] in ['public', 'published']:
                result_update_edit_log = JourneyRepository.toggle_no_edits(journey_id, no_edits)

        # Handle cover image
        cover_image_path = journey['cover_image']  # Keep existing cover image by default
        cover_image_changed = False

        # Check if user can delete cover image
        # - Journey owners can delete if they have delete permission (all users have this)
        # - Staff can delete others' cover images if they have delete permission AND journey doesn't have no_edits flag
        can_delete_cover = (is_owner and has_permission('delete_journey_cover')) or \
                          (not is_owner and has_permission('delete_journey_cover') and role in ['admin', 'editor', 'support_tech'] and journey['no_edits'] != 1)

        # Check if user can upload cover image (only owners with create permission)
        can_upload_cover = is_owner and has_permission('create_journey_cover')

        if can_delete_cover:
            # Delete the cover image
            if 'remove_cover' in request.form and request.form['remove_cover'] == '1':
                if journey['cover_image']:
                    staff_remove_file = None
                    if edit_reason:
                        # Move the file to staff remove folder
                        staff_remove_folder = current_app.config['UPLOAD_FOLDER_STAFF_REMOVE_IMAGE']
                        source_path = os.path.join(current_app.static_folder, journey['cover_image'])
                        destination_path = os.path.join(current_app.static_folder, staff_remove_folder, os.path.basename(journey['cover_image']))
                        result = Utils.move_file(source_path, destination_path)
                        # rename
                        if result:
                            # Create unique filename
                            unique_id = uuid.uuid4().hex[:8]  # short unique ID
                            new_filename = f"staff_remove_{unique_id}_{os.path.basename(journey['cover_image'])}"
                            result = Utils.rename_file(destination_path, new_filename)
                            if result:
                                staff_remove_file = f"{staff_remove_folder}/{new_filename}"
                            else:
                                flash('Failed to rename file in staff remove folder', 'error')
                        else:
                            flash('Failed to move file to staff remove folder', 'error')
                    else:
                        # Delete the physical file
                        old_image_path = os.path.join(current_app.static_folder, journey['cover_image'])
                        Utils.remove_file(old_image_path)
                    cover_image_path = None
                    cover_image_changed = True
                    if edit_reason:
                        summary.append({'item': 'cover_image', 'old_value': staff_remove_file, 'new_value': None})

        if can_upload_cover:
            # Handle the new uploaded cover image
            if 'cover_image' in request.files:
                file = request.files['cover_image']
                if file and file.filename:
                    # Check file format first (before doing anything else)
                    if not Utils.allowed_file(file.filename):
                        allowed_formats = ', '.join(ext.upper() for ext in current_app.config['ALLOWED_EXTENSIONS'])
                        flash(f"Invalid file format. Please upload an image file with one of these formats: {allowed_formats}", 'error')
                        return redirect(url_for('journey.journey_detail', journey_id=journey_id, page_auth=page_auth, show_hidden=show_hidden))

                    # Check file size
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)  # Reset file pointer
                    if file_size > current_app.config['MAX_FILE_SIZE']:
                        max_size_mb = current_app.config['MAX_FILE_SIZE'] // (1024 * 1024)
                        flash(f"File size exceeds the {max_size_mb}MB limit. Please choose a smaller image.", 'error')
                        return redirect(url_for('journey.journey_detail', journey_id=journey_id, page_auth=page_auth, show_hidden=show_hidden))

                    # Create a new file name and save it
                    # Get the original file extension
                    original_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                    unique_id = uuid.uuid4().hex[:8]  # short unique ID
                    filename = f'journey_{journey_id}_cover_{unique_id}.{original_ext}'
                    file_path = os.path.join(current_app.static_folder, current_app.config['UPLOAD_FOLDER_JOURNEY'])

                    # Try to upload the file first (before deleting old image)
                    result = Utils.upload_file(file, file_path, filename)

                    if result:
                        # Only delete old cover image after successful upload
                        if journey['cover_image']:
                            old_image_path = os.path.join(current_app.static_folder, journey['cover_image'])
                            Utils.remove_file(old_image_path)

                        cover_image_path = f"{current_app.config['UPLOAD_FOLDER_JOURNEY']}/{filename}"
                        cover_image_changed = True
                        if edit_reason:
                            summary.append({'item': 'cover_image', 'old_value': os.path.basename(journey['cover_image']) if journey['cover_image'] else None, 'new_value': filename})
                    else:
                        allowed_formats = ', '.join(ext.upper() for ext in current_app.config['ALLOWED_EXTENSIONS'])
                        flash(f"Failed to upload cover image. Please ensure the file is a valid image format ({allowed_formats}) and try again.", 'error')
                        return redirect(url_for('journey.journey_detail', journey_id=journey_id, page_auth=page_auth, show_hidden=show_hidden))

        # Update the journey in the database
        if cover_image_changed:
            result = JourneyRepository.update_journey(user_id, title, description, start_date, sharing, journey_id, cover_image=cover_image_path)
            gamification_service.check_achievement(user_id, 15)  # Check for "Earn an Achievement When Adding a Cover Image to Five Journeys" achievement
        else:
            result = JourneyRepository.update_journey(user_id, title, description, start_date, sharing, journey_id)
        if result or result_update_edit_log:
            flash('Journey updated successfully', 'success')
            if sharing == 'public':
                gamification_service.check_achievement(user_id, 3)  # Check for "Creating the Journey as Public" achievement 
            if sharing == 'published':
                gamification_service.check_achievement(user_id, 14)  # Check for "First Journey a User Publishes on the Homepage" achievement
        if result_update_edit_log and is_owner and has_permission('create_no_edits_flag') and has_permission('view_own_no_edits_flag') and no_edits == '1':
                gamification_service.check_achievement(user_id, 11) # Check for "Create First "No Edit" Journey" achievement
            
        
        if edit_reason:
            if title != journey['title']:
                summary.append({'item': 'title', 'old_value': journey['title'], 'new_value': title})
            if description != journey['description']:
                summary.append({'item': 'description', 'old_value': journey['description'], 'new_value': description})
            if summary:
                summary_json = json.dumps(summary)
            else:
                summary_json = None
            if summary_json is None:
                # If no changes were made, just flash a message
                flash('No Change has been made!', 'success')
                edit_log_id = None
            else:
                edit_log_id = EditLogRepository.create_edit_log(journey_id, None, user_id, edit_reason, summary_json)
                if edit_log_id:
                    # Create an edit notification for the user
                    result = EditLogRepository.create_edit_notification(journey['user_id'], edit_log_id)
                    if result:
                        flash('Edit Log and notification created successfully', 'success')
                    else:
                        flash('Failed to create edit log and notification', 'error')
                else:
                    flash('Failed to create edit log', 'error')
    return redirect(url_for('journey.journey_detail', journey_id=journey_id))


""" A method that displays the journey details."""
@journey.route('/hide', methods=['POST'])
@requires_permission('hide_journey')
def hide_journey():
    user_id = session['user_id']
    role = session['role']

    if request.method=='POST' and 'journey_id' in request.form and 'is_hide' in request.form:
        journey_id = request.form['journey_id']
        is_hide = request.form['is_hide']
        page_auth = request.form['page_auth']
        show_hidden = request.form.get('show_hidden', '0')
        return_to_detail = request.form.get('return_to_detail', '0')

        # Get the journey to check if it belongs to the current user
        journey = JourneyRepository.get_journey(journey_id)

        # Check if journey exists
        if not journey:
            flash('Journey not found', 'error')
            return redirect(url_for('journey.list_journey', page_auth=page_auth, show_hidden=show_hidden))

        # Check if the user has permission to hide this journey
        # Staff cannot hide own journeys
        if journey['user_id'] == user_id:
            flash('Staff users cannot hide their own journeys', 'error')

            # Redirect based on where the request came from
            if return_to_detail == '1':
                return redirect(url_for('journey.journey_detail', journey_id=journey_id, page_auth=page_auth, show_hidden=show_hidden))
            else:
                return redirect(url_for('journey.list_journey', page_auth=page_auth, show_hidden=show_hidden))

        result = JourneyRepository.hide_journey(journey_id, is_hide)
        if result:
            if is_hide == '0':
                flash('Journey unhide successfully', 'success')
            else:
                flash('Journey hide successfully', 'success')
        else:
            if is_hide == '0':
                flash('Failed to unhide journey', 'error')
            else:
                flash('Failed to hide journey', 'error')

        # Return to detail page if requested
        if return_to_detail == '1':
            return redirect(url_for('journey.journey_detail', journey_id=journey_id, page_auth=page_auth, show_hidden=show_hidden))
        else:
            return redirect(url_for('journey.list_journey', page_auth=page_auth, show_hidden=show_hidden))

    return redirect(url_for('auth.landing'))


"""A method that deletes the journey from the database.
    The user can only delete their own journeys.
"""
@journey.route('/journey/delete', methods = ['POST'])
@requires_permission('delete_own_journey')
def delete_journey():
    user_id = session['user_id']
    role = session['role']
    if request.method=='POST' and 'journey_id' in request.form:
        journey_id = request.form['journey_id']
        page_auth = request.form['page_auth']
        show_hidden = request.form.get('show_hidden', '0')
        journey = JourneyRepository.get_journeys(role, user_id, '', journey_id)

        if not journey:
            flash(f'Journey [ {journey_id} ] not found', 'error')
            return redirect(url_for('journey.list_journey', page_auth=page_auth, show_hidden=show_hidden))

        # Check if the user is the owner of the journey
        if journey['user_id'] != user_id:
            # Only allow deletion of own journeys
            flash('You can only delete your own journeys', 'error')
            return render_template('access_denied.html'), 403

        result = JourneyRepository.delete_journey(journey_id)
        if result:
            flash('Journey deleted successfully', 'success')
        else:
            flash('Failed to delete journey', 'error')

        return redirect(url_for('journey.list_journey', page_auth=session['page_auth'], show_hidden=show_hidden))


""" A method that displays the user status update form.
    The user can only edit their own journeys or if they are an admin or editor.
"""
@journey.route('/journey/public/update_user_status', methods=['POST'])
@requires_permission('update_user_sharing')
def update_user_status():
    if request.method == 'POST' and 'user_id' in request.form and 'status' in request.form:
        role = session['role']
        user_id = request.form['user_id']
        new_status = request.form['status']
        page_auth = request.form['page_auth']
        show_hidden = request.form.get('show_hidden', '0')
        result = UserRepository.update_user(user_id, status=new_status)
        if result > 0:
            flash(f"The user's status has been successfully updated to '{new_status}'.", "success")
        else:
            flash('Failed to update user status', 'error')
        return redirect(url_for('journey.list_journey', page_auth=page_auth, show_hidden=show_hidden))

""" A method that displays the journey details page."""
@journey.route('/journey/<int:journey_id>', methods=['GET'])
@requires_permission('view_own_journey')
def journey_detail(journey_id):
    user_id = session['user_id']
    role = session['role']
    user = UserRepository.get_user(user_id=user_id)
    journey = JourneyRepository.get_journeys(role, user_id, '', journey_id)

    if not journey:
        flash('Journey not found', 'error')
        return redirect(url_for('journey.list_journey', page_auth='private'))

    # Check permissions
    if user_id != journey['user_id']:
        if journey['status'] == 'private' and not has_permission('view_others_private_journey'):
            return render_template('access_denied.html'), 403
        elif journey['status'] == 'public' and not has_permission('view_others_puclic_journey'):
            return render_template('access_denied.html'), 403
        elif journey['status'] == 'published' and not has_permission('view_others_published_journey'):
            return render_template('access_denied.html'), 403

    edit_logs = None
    edit_logs_unread_count = None
    unread_edit_log_ids = None
    # Mark notification as read for current user
    if has_permission('view_edit_log_notification'):
        notification_id = request.args.get('notification_id')
        if notification_id:
            EditNotificationRepository.mark_notification_as_read(session['user_id'], notification_id=notification_id)

    if has_permission('view_own_edit_log') or has_permission('view_others_edit_log'):
        gamification_service.check_achievement(session['user_id'], 10) # Check for "View the Complete Edit History of My Shared Journeys and Events" achievement
        edit_logs = EditLogRepository.get_edit_logs(journey_id, None)
        for edit_log in edit_logs:
            edit_log['summary'] = json.loads(edit_log['summary']) if edit_log['summary'] else None

        edit_logs_unread_count = EditNotificationRepository.get_unread_count(journey['user_id'], journey_id=journey_id)
        unread_edit_logs = EditNotificationRepository.get_unread_notifications(journey['user_id'], journey_id=journey_id)
        unread_edit_log_ids = [edit_log['edit_log_id'] for edit_log in unread_edit_logs]

    # Get events for this journey
    events = EventRepository.get_event_list_details(journey_id)

    # Determine permissions for events
    can_create = False
    can_view = False
    can_edit = False
    staff_can_edit = False

    is_following_user = FollowRepository.view_follow_user(user_id, journey['user_id'])
    is_following_journey = FollowRepository.view_follow_journey(user_id, journey_id)

    if user_id == journey['user_id']:
        can_create = has_permission('create_own_event')
        can_view = has_permission('view_own_event')
        can_edit = has_permission('edit_own_event')
    else:
        if journey['status'] == 'public':
            can_view = has_permission('view_others_public_event')
            staff_can_edit = has_permission('edit_others_public_event')
        elif journey['status'] == 'published':
            can_view = has_permission('view_others_published_event')
            staff_can_edit = has_permission('edit_others_published_event')
        elif journey['status'] == 'private':
            can_view = has_permission('view_others_private_event')
            staff_can_edit = has_permission('edit_others_private_event')

    # Calculate cover image permissions
    is_owner = user_id == journey['user_id']
    role = session.get('role')
    # - Journey owners can delete if they have delete permission (all users have this)
    # - Staff can delete others' cover images if they have delete permission AND journey doesn't have no_edits flag
    can_delete_cover = (is_owner and has_permission('delete_journey_cover')) or \
                      (not is_owner and has_permission('delete_journey_cover') and role in ['admin', 'editor', 'support_tech'] and journey['no_edits'] != 1)
    can_upload_cover = is_owner and has_permission('create_journey_cover')

    # record the journey view for gamification
    GamificationRepository.create_journey_view(user_id, journey_id, journey['status'])
    gamification_service.check_achievement(user_id, 6, journey_id)  # Check for "View a Newly Shared Journey" achievement
    return render_template('journey_detail.html',
                         journey=journey,
                         events=events,
                         user=user,
                         can_create=can_create,
                         can_view=can_view,
                         can_edit=can_edit,
                         staff_can_edit=staff_can_edit,
                         is_following_user=is_following_user,
                         is_following_journey=is_following_journey,
                         edit_logs=edit_logs,
                         edit_logs_unread_count=edit_logs_unread_count,
                         unread_edit_log_ids=unread_edit_log_ids,
                         can_delete_cover=can_delete_cover,
                         can_upload_cover=can_upload_cover)