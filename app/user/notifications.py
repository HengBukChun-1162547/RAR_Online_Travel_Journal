from app.user import user
from app.auth.view import requires_permission, has_permission
from flask import session, flash, current_app, jsonify, request
from app.model import *

@user.route('/api/announcements/unread-count', methods=['GET'])
@requires_permission('view_announcements')
def get_unread_announcements_count():
    """
    Get the number of unread announcements for the current user.
    - Returns JSON response.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
    
    count = AnnouncementRepository.get_unread_announcements_count(session['user_id'])
    
    return jsonify({
        'success': True,
        'count': count
    })

@user.route('/api/announcements/unread', methods=['GET'])
@requires_permission('view_announcements')
def get_unread_announcements():
    """
    API endpoint to get unread announcements for the current user.
    Returns both count and announcement details.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
    
    try:
        # Get unread announcement IDs
        unread_ids = AnnouncementRepository.get_unread_announcement_ids(session['user_id'])
        
        # Get details for unread announcements
        announcements = []
        if unread_ids:
            announcements = AnnouncementRepository.get_unread_announcements(unread_ids)
        
        return jsonify({
            'success': True,
            'count': len(unread_ids),
            'announcements': announcements
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving unread announcements: {str(e)}'
        }), 500

@user.route('/api/subscriptionnotifications/unread', methods=['GET'])
@requires_permission('view_own_system_notification')
def get_unread_system_notifications():
    """
    API endpoint to get unread subscription expired notifications for the current user.
    Returns both count and expired subscription notification details.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
    
    try:
        # Get unread notification IDs
        unread_ids = NotificationRepository.get_unread_system_notification_ids(session['user_id'])
        
        subscription_expiry_notification_list = []
        # Get details for unread notifications
        if unread_ids:
            for sub_id in unread_ids:
                notification = NotificationRepository.get_unread_system_notification_details(sub_id['notification_id'])
                subscription_expiry_notification_list.append(notification[0])
        
        return jsonify({
            'success': True,
            'count': len(unread_ids),
            'notification_list': subscription_expiry_notification_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving unread system expired notifications: {str(e)}'
        }), 500

@user.route('/api/subscriptionnotifications/unread-count', methods=['GET'])
@requires_permission('view_own_system_notification')
def get_unread_system_notifications_count():
    """
    Get the count of unread subscription notifications for the current user.
    - Returns JSON response.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
    
    try:
        unread_ids = NotificationRepository.get_unread_system_notification_ids(session['user_id'])
        count = len(unread_ids) if unread_ids else 0
        
        return jsonify({
            'success': True,
            'count': count
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving unread system notification count: {str(e)}'
        }), 500

@user.route('/api/subscriptionnotifications/mark-as-read', methods=['POST'])
@requires_permission('view_own_system_notification')
def api_mark_subscription_notification_as_read():
    """API endpoint to mark a single subscription notification as read for the current user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    data = request.get_json()
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({'success': False, 'message': 'No notification ID provided'})
    
    result = NotificationRepository.mark_system_notifications_as_read(session['user_id'], notification_id)
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to mark notification as read'})

@user.route('/api/editnotifications/unread', methods=['GET'])
@requires_permission('view_edit_log_notification')
def get_unread_edit_notifications():
    """
    API endpoint to get unread edit notifications for the current user.
    Returns both count and notification details.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
    
    if not has_permission('view_edit_log_notification'):
        return jsonify({'success': False, 'message': 'Permission denied.'}), 403
    
    try:
        # Get unread edit notifications
        notifications = EditNotificationRepository.get_unread_notifications(session['user_id'])
        
        return jsonify({
            'success': True,
            'count': len(notifications),
            'notifications': notifications
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving unread edit notifications: {str(e)}'
        }), 500

@user.route('/api/editnotifications/unread-count', methods=['GET'])
@requires_permission('view_edit_log_notification')
def get_unread_edit_notifications_count():
    """
    Get the count of unread edit notifications for the current user.
    - Returns JSON response.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
    
    if not has_permission('view_edit_log_notification'):
        return jsonify({'success': False, 'message': 'Permission denied.'}), 403
    
    try:
        count = EditNotificationRepository.get_unread_count(session['user_id'])
        
        return jsonify({
            'success': True,
            'count': count
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving unread edit notification count: {str(e)}'
        }), 500
    
@user.route('/api/notifications/mark-all-read', methods=['POST'])
@requires_permission('view_announcements')
def mark_all_notifications_read():
    """
    Mark all types of notifications as read for the current user.
    Includes announcements, subscription notifications, and edit notifications.
    - Returns JSON response.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
    
    success = True
    total_count = 0
    error_messages = []
    
    # Mark announcements as read
    if has_permission('view_announcements'):
        try:
            count = AnnouncementRepository.mark_all_announcements_as_read(session['user_id'])
            total_count += count
        except Exception as e:
            success = False
            error_messages.append(f'Error marking announcements: {str(e)}')
    
    # Mark subscription notifications as read
    if has_permission('view_own_system_notification'):
        try:
            count = NotificationRepository.mark_all_system_notifications_as_read(session['user_id'])
            total_count += count
        except Exception as e:
            success = False
            error_messages.append(f'Error marking subscription notifications: {str(e)}')
    
    # Mark edit notifications as read
    if has_permission('view_edit_log_notification') and has_permission('view_own_edit_log'):
        try:
            count = EditNotificationRepository.mark_all_as_read(session['user_id'])
            total_count += count
        except Exception as e:
            success = False
            error_messages.append(f'Error marking edit notifications: {str(e)}')
    
    # Handle response
    if success:
        # flash(f'Marked {total_count} notifications as read.', 'success')
        return jsonify({
            'success': True,
            'message': f'Marked {total_count} notifications as read.',
            'count': total_count
        })
    else:
        error_message = ' '.join(error_messages)
        flash(f'Error marking some notifications as read: {error_message}', 'warning')
        return jsonify({
            'success': False,
            'message': error_message,
            'count': total_count
        })
    
@user.route('/api/announcements/mark-all-read', methods=['POST'])
@requires_permission('view_announcements')
def api_mark_all_announcements_read():
    """API endpoint to mark all announcements as read for the current user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    result = AnnouncementRepository.mark_all_announcements_as_read(session['user_id'])
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to mark announcements as read'})

@user.route('/api/systemnotifications/mark-all-read', methods=['POST'])
@requires_permission('view_own_system_notification')
def api_mark_all_system_notifications_read():
    """API endpoint to mark all system notifications as read for the current user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    result = NotificationRepository.mark_all_system_notifications_as_read(session['user_id'])
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to mark system notifications as read'})
    
@user.route('/api/editlogs/mark-as-read', methods=['POST'])
@requires_permission('view_edit_log_notification')
def api_mark_edit_log_as_read():
    """API endpoint to mark a single edit log as read for the current user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    data = request.get_json()
    edit_log_id = data.get('edit_log_id')
    
    if not edit_log_id:
        return jsonify({'success': False, 'message': 'No edit log ID provided'})
    edit_log = EditLogRepository.get_edit_log_by_log_id(edit_log_id)
    journey = JourneyRepository.get_journeys(session['role'], session['user_id'], None, journey_id=edit_log['journey_id'])
    if session['user_id'] != journey['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    result = EditNotificationRepository.mark_notification_as_read(session['user_id'], edit_log_id=edit_log_id)
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to mark edit log as read'})

@user.route('/api/editlogs/mark-all-read', methods=['POST'])
@requires_permission('view_edit_log_notification')
def api_mark_all_edit_logs_read():
    """API endpoint to mark all edit logs of a journey as read for the current user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    edit_log_ids = EditLogRepository.get_edit_logs_by_journey_user(session['user_id'])
    log_ids = [log['edit_log_id'] for log in edit_log_ids]
    result = EditNotificationRepository.mark_all_as_read(session['user_id'], edit_log_ids=log_ids)
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to mark edit logs as read'})
    
@user.route('/api/editlogs_history/mark-all-read', methods=['POST'])
@requires_permission('view_edit_log_notification')
def api_mark_all_event_edit_logs_read():
    """API endpoint to mark all event edit logs as read for the current user."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    data = request.get_json()
    journey_id = data.get('journey_id')
    event_id = data.get('event_id')

    if not event_id and not journey_id:
        return jsonify({'success': False, 'message': 'No Journey ID or Event ID provided'})

    edit_log_ids = EditLogRepository.get_edit_logs_by_journey_user(session['user_id'], journey_id=journey_id, event_id=event_id)
    log_ids = [log['edit_log_id'] for log in edit_log_ids]
    result = EditNotificationRepository.mark_all_as_read(session['user_id'], edit_log_ids=log_ids)
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to mark edit logs as read'})