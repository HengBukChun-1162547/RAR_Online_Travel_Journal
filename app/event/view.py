from flask import Blueprint, render_template, flash, redirect, url_for, request, session, current_app
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app import db, Utils
from app.auth.view import requires_permission, has_permission
from app.model import *
from app.gamification.view import gamification_service
import uuid
import json

event = Blueprint('event', __name__)

def check_event_permissions(event_data, journey_data=None):
    """
    Check if the current user has permission to view/edit/delete/manage the event
    """
    user_id = session.get('user_id')
    user_role = session.get('role')

    # Basic information
    is_event_owner = event_data['user_id'] == user_id if 'user_id' in event_data else False
    is_journey_owner = event_data.get('journey_owner_id') == user_id
    is_editor = user_role == 'editor'
    is_admin = user_role == 'admin'
    is_support_tech = user_role == 'support_tech'
    is_staff = is_editor or is_admin or is_support_tech

    # Journey status
    journey_is_public = False
    journey_is_hidden = False
    journey_is_published = False
    journey_no_edits = False

    if journey_data:
        journey_is_public = journey_data.get('status') == 'public'
        journey_is_hidden = journey_data.get('hidden')
        journey_is_published = journey_data.get('status') == 'published'
        journey_no_edits = journey_data.get('no_edits') == 1
    elif 'status' in event_data and 'hidden' in event_data:
        journey_is_public = event_data['status'] == 'public'
        journey_is_hidden = event_data['hidden']
        journey_is_published = event_data['status'] == 'published'
        journey_no_edits = event_data.get('no_edits') == 1

    # View permissions
    # Can view if:
    # 1. User owns the journey, OR
    # 2. Journey is public but not hidden OR
    # 3. Staff can view public but hidden journeys
    can_view = is_journey_owner or (journey_is_public and not journey_is_hidden) or (journey_is_published and not journey_is_hidden) or (is_staff and journey_is_public and journey_is_hidden) or (is_staff and journey_is_published and journey_is_hidden)

    # Edit permissions
    # Base edit permission - can edit own events
    can_edit = is_event_owner

    # Journey owner can edit events in journey
    if is_journey_owner:
        can_edit = True

    # Staff can edit public journey events (limited to title, description, location)
    # UNLESS the journey has no_edits flag enabled
    can_edit_public = is_staff and (journey_is_public or journey_is_published) and not journey_no_edits

    # Staff editing restrictions
    is_staff_editing_public = is_staff and not is_event_owner and not is_journey_owner and (journey_is_public or journey_is_published) and not journey_no_edits

    # Delete permissions (same as edit)
    can_delete = can_edit or (is_staff and (journey_is_public or journey_is_published) and not journey_no_edits)

    # Photo management
    can_delete_photo = can_edit or (is_staff and (journey_is_public or journey_is_published) and not journey_no_edits)
    can_add_photo = is_event_owner or is_journey_owner  # Only event/journey owners can add photos

    # Create permission (only journey owner)
    can_create = is_journey_owner

    return {
        'is_event_owner': is_event_owner,
        'is_journey_owner': is_journey_owner,
        'is_editor': is_editor,
        'is_admin': is_admin,
        'is_staff': is_staff,
        'journey_is_public': journey_is_public,
        'journey_is_hidden': journey_is_hidden,
        'journey_is_published': journey_is_published,
        'can_view': can_view,
        'can_edit': can_edit,
        'can_edit_public': can_edit_public,
        'is_staff_editing_public': is_staff_editing_public,
        'can_delete': can_delete,
        'can_delete_photo': can_delete_photo,
        'can_add_photo': can_add_photo,
        'can_create': can_create

    }

@event.route('/event/new/<int:journey_id>', methods=['GET', 'POST'])
@requires_permission('create_own_event')
def new_event(journey_id):
    """Add a new event to a journey"""
    # Check if journey exists and user has permission
    journey = JourneyRepository.get_journey(journey_id)

    if not journey:
        flash('Journey not found', 'error')
        return redirect(url_for('journey.list_journey'))

    # Check permissions
    journey_data = {
        'status': journey['status'],
        'hidden': journey['hidden'],
        'no_edits': journey['no_edits']
    }
    permissions = check_event_permissions({'journey_owner_id': journey['user_id']}, journey_data)

    # Only the journey owner can add events
    if not permissions['can_create']:
        return render_template('access_denied.html'), 403

    # Get all locations for dropdown
    locations = LocationRepository.get_locations()
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description', '')
        start_date_str = request.form.get('start_date')
        start_time_str = request.form.get('start_time')
        end_date_str = request.form.get('end_date')
        end_time_str = request.form.get('end_time')
        location_id = request.form.get('location_id')
        location_new = request.form.get('location_new')

        # Validate required fields
        errors = []
        if not title:
            errors.append('Title is required')
        if not start_date_str:
            errors.append('Start date is required')
        if not start_time_str:
            errors.append('Start time is required')
        if not location_id and not location_new:
            errors.append('Location is required')

        # Parse dates and times
        try:
            start_date = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")

            # Get journey start date (which is a date object, not datetime)
            journey_start_date = journey['start_date']

            # Convert journey start date to datetime at midnight for comparison
            journey_start_datetime = datetime.combine(journey_start_date, datetime.min.time())

            # Ensure event start date is not before journey start date
            if start_date < journey_start_datetime:
                errors.append(f'Event date cannot be earlier than the journey start date ({journey_start_date.strftime("%Y-%m-%d")})')

            if end_date_str and end_time_str:
                end_date = datetime.strptime(f"{end_date_str} {end_time_str}", "%Y-%m-%d %H:%M")
                # Validate end time is after start time
                if end_date <= start_date:
                    errors.append('End time must be later than start time')
            else:
                end_date = None
        except ValueError:
            errors.append('Invalid date or time format')

        # Create new location if needed
        if location_new and not location_id:
            # Check if location already exists
            existing_location = LocationRepository.get_locations(name=location_new)

            if existing_location:
                location_id = existing_location['location_id']
            else:
                # Create new location
                location_id = LocationRepository.add_location(location_new)

        # If no errors, create the event
        if not errors:
            user_id = session.get('user_id')
            event_data={'journey_id': journey_id, 'user_id': user_id, 'location_id': location_id, 'title': title, 'description': description, 'start_date': start_date, 'end_date': end_date, 'update_by': user_id}
            try:
                # Insert the event and Get the new event_id
                event_id = EventRepository.add_event(event_data)

                # Handle photo upload
                if 'photo' in request.files:
                    uploaded_files = request.files.getlist('photo')
                    if len(uploaded_files) > 1 and not has_permission('add_multiple_photos'):
                        flash('You can only upload one photo at a time.', 'error')
                        return redirect(url_for('event.event_detail', event_id=event_id))
                    if not uploaded_files:
                        flash('No files selected', 'error')
                        return redirect(url_for('event.event_detail', event_id=event_id))
                    elif len(uploaded_files) > current_app.config['MAX_EVENT_IMAGE_COUNT']:
                        flash(f'You can only upload up to {current_app.config["MAX_EVENT_IMAGE_COUNT"]} photos in total.', 'error')
                        return redirect(url_for('event.event_detail', event_id=event_id))
                    
                    for file in uploaded_files:
                        if file and file.filename:
                            if Utils.allowed_file(file.filename):
                                try:
                                    filename = secure_filename(file.filename)
                                    # Create unique filename
                                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                                    unique_id = uuid.uuid4().hex[:8]  # short unique ID
                                    new_filename = f"event_{event_id}_{unique_id}.{file_ext}"

                                    # Save the file
                                    upload_folder = os.path.join(current_app.static_folder, current_app.config['UPLOAD_FOLDER_EVENT'])
                                    Utils.upload_file(file, upload_folder, new_filename)
                                    # Update event with image path
                                    EventRepository.update_event(event_id, isNew=True, image_path=f"{current_app.config['UPLOAD_FOLDER_EVENT']}/{new_filename}")
                                except Exception as e:
                                    flash(f'Error saving photo: {str(e)}', 'error')
                            else:
                                allowed_list = ', '.join(ext.upper() for ext in current_app.config['ALLOWED_EXTENSIONS'])
                                flash(f'Invalid file type. Only {allowed_list} files are allowed.', 'error')
                gamification_service.check_achievement(user_id, 2) # Check for "Creating the First Event" achievement
                gamification_service.check_achievement(user_id, 4) # Check for "Visit More Than 20 Locations" achievement
                flash('Successfully added the new event', 'success')
                return redirect(url_for('journey.journey_detail', journey_id=journey_id))
            except Exception as e:
                flash(f'Error creating event: {str(e)}', 'error')

        for error in errors:
            flash(error, 'error')

    return render_template(
        'event_form.html',
        journey=journey,
        locations=locations,
        is_new=True
    )

@event.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@requires_permission('edit_own_event')
def edit_event(event_id):
    """Edit an existing event"""
    # Get event details
    event = EventRepository.get_event_details(event_id=event_id)
    event_images = EventRepository.get_event_images(event_id)

    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('journey.list_journey'))

    # Check if journey exists and user has permission
    journey = JourneyRepository.get_journey(event["journey_id"])

    if not journey:
        flash('Journey not found', 'error')
        return redirect(url_for('journey.list_journey'))

    # Check permissions
    journey_data = {
        'status': event['status'],
        'hidden': event['hidden'],
        'no_edits': journey['no_edits']
    }
    permissions = check_event_permissions(event, journey_data)

    # Check if user can edit this event
    if not (permissions['can_edit'] or permissions['can_edit_public']):
        return render_template('access_denied.html'), 403

    # Format dates for the form
    if event['start_date']:
        start_datetime = event['start_date']
        event['start_date_input'] = start_datetime.strftime('%Y-%m-%d')
        event['start_time_input'] = start_datetime.strftime('%H:%M')

    if event['end_date']:
        end_datetime = event['end_date']
        event['end_date_input'] = end_datetime.strftime('%Y-%m-%d')
        event['end_time_input'] = end_datetime.strftime('%H:%M')

    # Get all locations for dropdown
    locations = LocationRepository.get_locations()

    # Get current location name
    current_location = LocationRepository.get_locations(location_id=event['location_id'])
    if current_location:
        event['location_name'] = current_location['name']

    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        start_date_str = request.form.get('start_date')
        start_time_str = request.form.get('start_time')
        end_date_str = request.form.get('end_date')
        end_time_str = request.form.get('end_time')
        location_id = request.form.get('location_id')
        location_new = request.form.get('location_new', '').strip()

        # Validate required fields
        errors = []
        if not title:
            errors.append('Title is required')

        # Only check date/time fields if not staff editing public event
        if not permissions['is_staff_editing_public']:
            if not start_date_str:
                errors.append('Start date is required')
            if not start_time_str:
                errors.append('Start time is required')

        if not location_id and not location_new:
            errors.append('Location is required')

        # Parse dates and times
        try:
            if not permissions['is_staff_editing_public']:
                start_date = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")

                # Get journey start date for validation
                journey_start_date = journey['start_date']
                journey_start_datetime = datetime.combine(journey_start_date, datetime.min.time())

                # Ensure event start date is not before journey start date
                if start_date < journey_start_datetime:
                    errors.append(f'Event date cannot be earlier than the journey start date ({journey_start_date.strftime("%Y-%m-%d")})')

                if end_date_str and end_time_str:
                    end_date = datetime.strptime(f"{end_date_str} {end_time_str}", "%Y-%m-%d %H:%M")
                    # Validate end time is after start time
                    if end_date <= start_date:
                        errors.append('End time must be later than start time')
                else:
                    end_date = None
            else:
                # Staff editing public event - keep original dates
                start_date = event['start_date']
                end_date = event['end_date']
                if 'staff_reason' in request.form:
                    edit_reason = request.form['staff_reason']
                    summary = []
                else:
                    edit_reason = None
        except ValueError:
            errors.append('Invalid date or time format')

        # Create new location if needed
        if location_new and not location_id:
            # Check if location already exists
            existing_location = LocationRepository.get_locations(name=location_new)

            if existing_location:
                location_id = existing_location['location_id']
            else:
                # Create new location
                location_id = LocationRepository.add_location(location_new)
                if location_id == -1:
                    errors.append('Failed to create new location')

        # If no errors, update the event
        if not errors:
            user_id = session.get('user_id')
            event_data = {
                'location_id': location_id,
                'title': title,
                'description': description,
                'start_date': start_date,
                'end_date': end_date,
                'update_by': user_id
            }

            try:
                # If staff editing public event, only update title, description, location
                result = EventRepository.update_event_data(event_id, permissions['is_staff_editing_public'], event_data)

                if result == -1:
                    flash("Failed to update event data", 'error')
                    return redirect(url_for('event.event_detail', event_id=event_id))
                
                # If staff editing public event, update the reason for edit 
                if permissions['is_staff_editing_public']:
                    if int(location_id) != int(event['location_id']):
                        new_value = LocationRepository.get_locations(location_id=location_id)
                        summary.append({'item': 'Location', 'old_value': event['location_name'], 'new_value': new_value['name']})
                    if title != event['title']:
                        summary.append({'item': 'Title', 'old_value': event['title'], 'new_value': title})
                    if description != event['description']:
                        summary.append({'item': 'Description', 'old_value': event['description'], 'new_value': description})
                    
                    if summary:
                        summary_json = json.dumps(summary)
                    else:
                        summary_json = None
                    edit_log_id = EditLogRepository.create_edit_log(journey['journey_id'], event_id, user_id, edit_reason, summary_json)
                    if edit_log_id:
                        result = EditLogRepository.create_edit_notification(journey['user_id'], edit_log_id)
                        if result:
                            flash('Edit Log and notification created successfully', 'success')
                        else:
                            flash('Failed to create edit log and notification', 'error')
                    else:
                        flash('Failed to create edit log', 'error')

                # Handle photo upload - but not for staff editing public events unless it's photo removal
                if 'photo' in request.files and permissions['can_add_photo']:
                    file = request.files['photo']
                    if file and file.filename:
                        if Utils.allowed_file(file.filename):
                            try:
                                # Check file size
                                file.seek(0, os.SEEK_END)
                                file_size = file.tell()
                                file.seek(0)  # Reset file pointer

                                if file_size > current_app.config['MAX_FILE_SIZE']:
                                    flash(f"File is too large. Maximum size is {current_app.config['MAX_FILE_SIZE'] // (1024 * 1024)}MB.", 'error')
                                else:
                                    filename = secure_filename(file.filename)
                                    # Create unique filename using event_id
                                    file_ext = filename.rsplit('.', 1)[1].lower()
                                    new_filename = f"event_{event_id}.{file_ext}"

                                    # Remove existing image if any
                                    if event['event_image']:
                                        old_path = os.path.join(current_app.static_folder, event['event_image'])
                                        Utils.remove_file(old_path)

                                    # Save the file
                                    upload_folder = os.path.join(current_app.static_folder, current_app.config['UPLOAD_FOLDER_EVENT'])
                                    Utils.upload_file(file, upload_folder, new_filename)

                                    # Update event with image path
                                    image_path = f"{current_app.config['UPLOAD_FOLDER_EVENT']}/{new_filename}"
                                    result = EventRepository.update_event(event_id, isNew=False, image_path=image_path)

                                    if result == -1:
                                        raise Exception("Failed to update event image")

                            except Exception as e:
                                flash(f'Error saving photo: {str(e)}', 'error')
                        else:
                            allowed_list = ', '.join(ext.upper() for ext in current_app.config['ALLOWED_EXTENSIONS'])
                            flash(f'Invalid file type. Only {allowed_list} files are allowed.', 'error')
                gamification_service.check_achievement(user_id, 4) # Check for "Visit More Than 20 Locations" achievement
                flash('Successfully updated the event', 'success')
                return redirect(url_for('event.event_detail', event_id=event['event_id']))
            except Exception as e:
                flash(f'Error updating event: {str(e)}', 'error')

        for error in errors:
            flash(error, 'error')

    return render_template(
        'event_form.html',
        event=event,
        event_images=event_images,
        journey=journey,
        locations=locations,
        is_new=False,
        is_staff_editing_public=permissions['is_staff_editing_public']
    )

@event.route('/event/detail/<int:event_id>', methods=['GET', 'POST'])
@requires_permission('view_own_event')
def event_detail(event_id):
    """Display detailed view of an event"""
    # Get event details
    event = EventRepository.get_event_locaiton_details(event_id)
    event_images = EventRepository.get_event_images(event_id)

    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('journey.list_journey'))

    # Get journey to check no_edits flag
    journey = JourneyRepository.get_journey(event['journey_id'])

    # Check permissions
    journey_data = {
        'status': event['status'],
        'hidden': event['hidden'],
        'no_edits': journey['no_edits'] if journey else 0
    }
    permissions = check_event_permissions(event, journey_data)

    if not permissions['can_view']:
        return render_template('access_denied.html'), 403

    can_view_multiple_photos = False
    user = UserRepository.get_user(event['user_id'])
    if has_permission('add_multiple_photos', event['user_id']):
        can_view_multiple_photos = True

    is_following = LocationRepository.is_user_following_location(session['user_id'], event['location_id'])

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
        edit_logs = EditLogRepository.get_edit_logs(None, event['event_id'])
        for edit_log in edit_logs:
            edit_log['summary'] = json.loads(edit_log['summary']) if edit_log['summary'] else None

        edit_logs_unread_count = EditNotificationRepository.get_unread_count(event['journey_owner_id'], event_id=event_id)
        unread_edit_logs = EditNotificationRepository.get_unread_notifications(event['journey_owner_id'], event_id=event_id)
        unread_edit_log_ids = [edit_log['edit_log_id'] for edit_log in unread_edit_logs]

    return render_template(
        'event_detail.html',
        event=event,
        event_images=event_images,
        can_edit=permissions['can_edit'] or permissions['can_edit_public'],
        is_owner=permissions['is_event_owner'],
        is_staff=permissions['is_staff'],
        can_view_multiple_photos=can_view_multiple_photos,
        is_following_location=is_following,
        can_update=permissions['can_edit'],
        edit_logs=edit_logs,
        edit_logs_unread_count=edit_logs_unread_count,
        unread_edit_log_ids=unread_edit_log_ids
    )

@event.route('/event/delete/<int:event_id>', methods=['POST'])
@requires_permission('delete_own_event')
def delete_event(event_id):
    """Delete an event"""
    # Get event details
    event = EventRepository.get_event_details(event_id=event_id)

    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('journey.list_journey'))

    # Get journey to check no_edits flag
    journey = JourneyRepository.get_journey(event['journey_id'])

    # Check permissions
    journey_data = {
        'status': event['status'],
        'hidden': event['hidden'],
        'no_edits': journey['no_edits'] if journey else 0
    }
    permissions = check_event_permissions(event, journey_data)

    if not permissions['can_delete']:
        return render_template('access_denied.html'), 403

    try:
        # Delete the event and its photo
        # Remove the photo file if it exists
        # if event['event_image']:
        #     file_path = os.path.join(current_app.static_folder, event['event_image'])
        #     Utils.remove_file(file_path)

        # Delete the event from database
        EventRepository.delete_event(event_id)

        flash('Event has been deleted', 'success')
    except Exception as e:
        flash(f'Error deleting event: {str(e)}', 'error')

    return redirect(url_for('journey.journey_detail', journey_id=event['journey_id']))

@event.route('/event/photo/<int:event_id>', methods=['GET', 'POST'])
@requires_permission('add_single_photo')
def manage_photo(event_id):
    """Add or replace a photo for an event"""
    user_role = session['role']
    # Get event details
    event = EventRepository.get_event_details(event_id=event_id)
    event_images = EventRepository.get_event_images(event_id)

    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('journey.list_journey'))

    # Get journey to check no_edits flag
    journey = JourneyRepository.get_journey(event['journey_id'])

    # Check permissions
    journey_data = {
        'status': event['status'],
        'hidden': event['hidden'],
        'no_edits': journey['no_edits'] if journey else 0
    }
    permissions = check_event_permissions(event, journey_data)

    if not (permissions['can_delete_photo'] or permissions['can_add_photo']):
        return render_template('access_denied.html'), 403

    if request.method == 'POST':
        if 'delete_photo' in request.form and permissions['can_delete_photo']:
            # Remove photo
            image_path = request.form.get('image_path')
            if 'staff_photo_removal_reason' in request.form:
                edit_reason = request.form['staff_photo_removal_reason']
                summary = []
            else:
                edit_reason = None
            try:
                staff_remove_file = None
                if edit_reason:
                    # Move the file to staff remove folder
                    staff_remove_folder = current_app.config['UPLOAD_FOLDER_STAFF_REMOVE_IMAGE']
                    source_path = os.path.join(current_app.static_folder, image_path)
                    destination_path = os.path.join(current_app.static_folder, staff_remove_folder, os.path.basename(image_path))
                    result = Utils.move_file(source_path, destination_path)
                    # rename
                    if result:
                        new_filename = f"staff_remove_{os.path.basename(image_path)}"
                        result = Utils.rename_file(destination_path, new_filename)
                        if result:
                            staff_remove_file = f"{staff_remove_folder}/{new_filename}"
                        else:
                            flash('Failed to rename file in staff remove folder', 'error')
                    else:
                        flash('Failed to move file to staff remove folder', 'error')
                else:
                    # Delete the file
                    file_path = os.path.join(current_app.static_folder, image_path)
                    Utils.remove_file(file_path)

                # Update database
                EventRepository.update_event(
                    event_id,
                    isNew=False,
                    image_path="NULL",
                    update_by=session.get('user_id'),
                    image_path_to_delete=image_path
                )
                # Create edit log for photo removal
                if edit_reason:
                    summary.append({'item': 'event_image', 'old_value': staff_remove_file, 'new_value': None})
                    summary_json = json.dumps(summary)
                    
                    edit_log_id = EditLogRepository.create_edit_log(event['journey_id'], event['event_id'], session['user_id'], edit_reason, summary_json)
                    if edit_log_id:
                        result = EditLogRepository.create_edit_notification(event['journey_owner_id'], edit_log_id)
                        if result:
                            flash('Edit Log and notification created successfully', 'success')
                        else:
                            flash('Failed to create edit log and notification', 'error')
                    else:
                        flash('Failed to create edit log', 'error')

                flash('Photo has been removed', 'success')
            except Exception as e:
                flash(f'Error removing photo: {str(e)}', 'error')

        elif 'upload_photos' in request.form and permissions['can_add_photo']:
            if user_role == 'traveller':
                if event_images:
                    flash("Travellers can only upload one image per event.", "danger")
                    return redirect(url_for('event.event_detail', event_id=event_id))
            uploaded_files = request.files.getlist('photos')
            if not uploaded_files:
                flash('No files selected', 'error')
            elif len(uploaded_files) + len(event_images) > current_app.config['MAX_EVENT_IMAGE_COUNT']:
                flash(f'You can only upload up to {current_app.config["MAX_EVENT_IMAGE_COUNT"]} photos in total.', 'error')
            else:
                try:
                    upload_folder = os.path.join(current_app.static_folder, current_app.config['UPLOAD_FOLDER_EVENT'])
                    os.makedirs(upload_folder, exist_ok=True)

                    for file in uploaded_files:
                        if file and file.filename and Utils.allowed_file(file.filename):
                            # Check file size
                            file.seek(0, os.SEEK_END)
                            file_size = file.tell()
                            file.seek(0)

                            if file_size > current_app.config['MAX_FILE_SIZE']:
                                flash(f"{file.filename} is too large. Max size: {current_app.config['MAX_FILE_SIZE'] // (1024 * 1024)}MB.", 'error')
                                continue

                            # Create unique filename
                            file_ext = file.filename.rsplit('.', 1)[1].lower()
                            unique_id = uuid.uuid4().hex[:8]  # short unique ID
                            new_filename = f"event_{event_id}_{unique_id}.{file_ext}"

                            # Save file
                            Utils.upload_file(file, upload_folder, new_filename)

                            # Save relative path in DB
                            rel_path = f"{current_app.config['UPLOAD_FOLDER_EVENT']}/{new_filename}"
                            EventRepository.update_event(event_id, isNew=True, image_path=rel_path, update_by=session.get('user_id'))

                        else:
                            flash(f"Invalid file or extension: {file.filename}", 'error')

                    flash('Photos uploaded successfully', 'success')
                except Exception as e:
                    flash(f'Error uploading photos: {str(e)}', 'error')

        elif 'change_photo' in request.form and permissions['can_add_photo']:
            # Handle image update
            old_image_path = request.form.get('old_image_path')
            image_id = request.form.get('image_id')
            file = request.files.get('new_image')


            if file and file.filename:
                if Utils.allowed_file(file.filename):
                    try:
                        # Check file size
                        file.seek(0, os.SEEK_END)
                        file_size = file.tell()
                        file.seek(0)  # Reset file pointer

                        if file_size > current_app.config['MAX_FILE_SIZE']:
                            flash(f"File is too large. Maximum size is {current_app.config['MAX_FILE_SIZE'] // (1024 * 1024)}MB.", 'error')
                        else:
                            old_path = os.path.join(current_app.static_folder, old_image_path)
                            Utils.remove_file(old_path)

                            filename = secure_filename(file.filename)
                            # Create unique filename using event_id
                            file_ext = filename.rsplit('.', 1)[1].lower()
                            new_filename = f"event_{event_id}_{image_id}.{file_ext}"

                            # Save the file
                            upload_folder = os.path.join(current_app.static_folder, current_app.config['UPLOAD_FOLDER_EVENT'])
                            Utils.upload_file(file, upload_folder, new_filename)

                            # Update event with image path
                            image_path = f"{current_app.config['UPLOAD_FOLDER_EVENT']}/{new_filename}"
                            EventRepository.update_event(event_id, isNew=False, image_path=image_path, image_id=image_id, update_by=session.get('user_id'))
                            flash('Photos uploaded successfully', 'success')

                    except Exception as e:
                        flash(f'Error saving photo: {str(e)}', 'error')
                else:
                    allowed_list = ', '.join(ext.upper() for ext in current_app.config['ALLOWED_EXTENSIONS'])
                    flash(f'Invalid file type. Only {allowed_list} files are allowed.', 'error')


        elif not permissions['can_add_photo'] and 'photo' in request.files:
            return render_template('access_denied.html'), 403

        return redirect(url_for('event.event_detail', event_id=event_id))

    return render_template(
        'manage_photo.html',
        event=event,
        event_images=event_images,
        can_delete_photo=permissions['can_delete_photo'],
        can_add_photo=permissions['can_add_photo']
    )

@event.route('/manage_locations', methods=['GET'])
@requires_permission('manage_locations')
def manage_locations():
    """Manage locations"""
    search_term = request.args.get('search', '')
    locations = LocationRepository.get_all_locations(search_term)
    all_locations = LocationRepository.get_all_locations()

    return render_template('manage_locations.html',
                          locations=locations,
                          all_locations=all_locations,
                          search_term=search_term,
                          user=session)

@event.route('/merge_locations', methods=['POST'])
@requires_permission('manage_locations')
def merge_locations_route():
    """Merge locations"""
    source_location_ids = request.form.getlist('source_location_ids')
    target_type = request.form.get('target_type')

    if not source_location_ids:
        flash('Please select at least one source location to merge', 'error')
        return redirect(url_for('event.manage_locations'))

    # Handle target location based on the selection type
    if target_type == 'existing':
        target_location_id = request.form.get('target_location_id')
        if not target_location_id:
            flash('Please select a target location', 'error')
            return redirect(url_for('event.manage_locations'))
    else:  # target_type == 'new'
        # Create a new location
        new_location_name = request.form.get('new_location_name')
        if not new_location_name:
            flash('New location name is required', 'error')
            return redirect(url_for('event.manage_locations'))

        result = LocationRepository.add_location(new_location_name)
        if result == -1:
            flash(f'Error creating new location: {result}', 'error')
            return redirect(url_for('event.manage_locations'))

        target_location_id = result

    # Perform the merge operation
    success, result = LocationRepository.merge_locations(source_location_ids, target_location_id)

    if success:
        message = f'Successfully merged locations. Updated {result["updated_events"]} events and deleted {result["deleted_locations"]} locations.'
        if result["skipped_locations"] > 0:
            message += f' (Skipped {result["skipped_locations"]} locations that were the same as the target)'
        flash(message, 'success')
    else:
        flash(f'Error merging locations: {result}', 'error')

    return redirect(url_for('event.manage_locations'))


@event.route('/events')
@requires_permission('view_own_event')
def events():
    """List all events in a specific journey"""
    # Identify the journey
    journey_id = request.args.get('journey_id')
    # Show all the event items in selected journey
    journey = JourneyRepository.get_journey(journey_id)

    # Error handling when journey does not exist
    if not journey:
        flash('This journey does not existed', 'error')
        return redirect(url_for('journey.list_journey'))

    event = EventRepository.get_event_list_details(journey_id)

    # Identify the user's authorization
    journey_data = {
        'status': journey['status'],
        'hidden': journey['hidden'],
        'no_edits': journey['no_edits']
    }
    permissions = check_event_permissions({'journey_owner_id': journey['user_id']}, journey_data)
    is_following = LocationRepository.is_user_following_location(session['user_id'], event['location_id'])

    if not permissions['can_view']:
        return render_template('access_denied.html'), 403

    return render_template('events.html',
                           events = event,
                           journey = journey,
                           can_view = permissions['can_view'],
                           can_create = permissions['can_create'],
                           can_edit = permissions['can_edit'],
                           staff_can_edit = permissions['is_staff_editing_public'], is_following_location=is_following)

