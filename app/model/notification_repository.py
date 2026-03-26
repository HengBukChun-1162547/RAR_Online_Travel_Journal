from flask import flash
from app import db

class NotificationRepository:
    """Repository class for managing notifications."""
    
    
    @staticmethod    
    def get_expiring_subscription_details():
        """ Get expiring subscriptions in the next 7 days"""
        try:
            str_sql = """
                        SELECT subscription_id, user_id, subscription_type, expiry_date, 
                        DATEDIFF(expiry_date, CURDATE()) AS days_remaining
                        FROM subscriptions
                        WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                        ORDER BY expiry_date DESC;
                    """
            params = []
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving expiring subscriptions: {e}")
            return None
        
        finally:
            db.close_db()
    
    @staticmethod
    def create_system_notification(user_id, message, type):
        """ Create notifications for system """
        
        try:
            str_sql = """ INSERT INTO system_notifications(user_id, message, type)
                    VALUES (%s, %s, %s) """
                    
            params = []
            params.append(user_id)
            params.append(message)
            params.append(type)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating system notification: {e}")
            return None
        
        finally:
            db.close_db()
    
    @staticmethod    
    def get_unread_system_notification_ids(user_id):
        """ Get expiring system notification ids"""
        try:
            str_sql = """
                        SELECT notification_id FROM system_notifications
                        where is_read = 0 and user_id = %s
                        ORDER BY created_at DESC
                    """
            params = [user_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving expiring system notification ids: {e}")
            return None

    @staticmethod    
    def get_system_notification_details(user_id):
        """ Get expiring system notification details"""
        try:
            str_sql = """
                        SELECT notification_id,message,created_at,is_read,type FROM system_notifications
                        where user_id = %s
                        ORDER BY created_at DESC
                    """
            params = [user_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving unread system notifications: {e}", "danger")
            return None
        
    @staticmethod    
    def get_unread_system_notification_details(unread_id):
        """ Get expiring system notification details"""
        try:
            str_sql = """
                        SELECT message,type,created_at,is_read FROM system_notifications
                        where is_read = 0 and notification_id = %s
                        ORDER BY created_at DESC
                    """
            params = [unread_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving unread system notifications: {e}", "danger")
            return None
        
    @staticmethod    
    def mark_all_system_notifications_as_read(user_id):
        """
        Mark all system notifications as read for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The number of notifications marked as read
        """
        try:
            # First get count of unread notifications
            count_sql = """
                SELECT COUNT(*) as count
                FROM system_notifications
                WHERE user_id = %s AND is_read = 0
            """
            
            update_sql = """
                UPDATE system_notifications
                SET is_read = 1
                WHERE user_id = %s AND is_read = 0
            """
            
            params = [user_id]
            count = 0
            
            with db.get_cursor() as cursor:
                cursor.execute(count_sql, params)
                result = cursor.fetchone()
                count = result['count'] if result else 0
                
                if count > 0:
                    cursor.execute(update_sql, params)
                
            return count
        except Exception as e:
            flash(f"Error marking all system notifications as read: {e}", "danger")
            return 0

    @staticmethod    
    def mark_system_notifications_as_read(user_id, notification_id):
        """
        Mark system notifications as read for a user.
        
        Args:
            user_id: The ID of the user
            notification_id: The ID of the notification
            
        Returns:
            The number of notifications marked as read
        """
        try:
            # First get count of unread notifications
            count_sql = """
                SELECT is_read
                FROM system_notifications
                WHERE user_id = %s AND notification_id = %s AND is_read = 0
            """
            
            update_sql = """
                UPDATE system_notifications
                SET is_read = 1
                WHERE user_id = %s AND notification_id = %s AND is_read = 0
            """
            
            params = [user_id, notification_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(count_sql, params)
                result = cursor.fetchone()
                
                if result:
                    cursor.execute(update_sql, params)
                    return cursor.rowcount
        except Exception as e:
            flash(f"Error marking system notifications as read: {e}", "danger")
            return -1

class EditNotificationRepository:
    """Repository class for managing edit notifications."""

    @staticmethod
    def get_unread_notifications(user_id, journey_id=None, event_id=None):
        """
        Get unread edit notifications for a user.
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of notifications to return
            
        Returns:
            A list of unread edit notifications
        """
        try:
            str_sql = """
                SELECT en.notification_id, en.user_id, en.edit_log_id, 
                       en.is_read, en.created_at, el.summary, 
                       el.journey_id, el.event_id, el.editor_id, el.edit_reason
                FROM edit_notifications en
                JOIN edit_logs el ON en.edit_log_id = el.edit_log_id
                WHERE en.user_id = %s AND en.is_read = 0
            """
            params = [user_id]
            
            if journey_id:
                str_sql += " AND el.journey_id = %s AND el.event_id IS NULL"
                params.append(journey_id)

            if event_id:
                str_sql += " AND el.event_id = %s"
                params.append(event_id)

            str_sql += """ ORDER BY en.created_at DESC """
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving unread edit notifications: {e}", "danger")
            return []
    
    @staticmethod
    def get_unread_count(user_id, journey_id=None, event_id=None):
        """
        Get the count of unread edit notifications for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The count of unread notifications
        """
        try:
            str_sql = """
                SELECT COUNT(*) as count
                FROM edit_notifications
                WHERE user_id = %s AND is_read = 0
            """
            params = [user_id]

            if journey_id:
                str_sql += " AND edit_log_id IN (SELECT edit_log_id FROM edit_logs WHERE journey_id = %s AND event_id IS NULL)"
                params.append(journey_id)
            
            if event_id:
                str_sql += " AND edit_log_id IN (SELECT edit_log_id FROM edit_logs WHERE event_id = %s)"
                params.append(event_id)

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            flash(f"Error counting unread edit notifications: {e}", "danger")
            return 0
    
    @staticmethod
    def mark_notification_as_read(user_id, notification_id=None, edit_log_id=None):
        try:
            # First check if already marked as read
            temp_id = ""
            if notification_id:
                str_check = """
                    SELECT is_read FROM edit_notifications
                    WHERE user_id = %s AND notification_id = %s AND is_read = 1
                """
                
                str_insert = """
                    UPDATE edit_notifications 
                    SET is_read = 1
                    WHERE user_id = %s AND notification_id = %s
                """
                temp_id = notification_id
            elif edit_log_id:
                str_check = """
                    SELECT is_read FROM edit_notifications
                    WHERE user_id = %s AND edit_log_id = %s AND is_read = 1
                """
                
                str_insert = """
                    UPDATE edit_notifications 
                    SET is_read = 1
                    WHERE user_id = %s AND edit_log_id = %s
                """
                temp_id = edit_log_id
            
            params = [user_id, temp_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_check, params)
                if cursor.fetchone():
                    return True  # Already marked as read
                    
                cursor.execute(str_insert, params)
                return cursor.rowcount > 0
        except Exception as e:
            flash(f"Error marking announcement as read: {e}", "danger")
            return False
        
    @staticmethod
    def mark_all_as_read(user_id, edit_log_ids=None):
        """
        Mark all edit notifications as read for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The number of notifications marked as read
        """
        try:
            params_1 = []
            params_2 = []
            # First get count of unread notifications
            if edit_log_ids:
                count_sql = """
                    SELECT COUNT(*) as count
                    FROM edit_notifications
                    WHERE user_id = %s AND is_read = 0
                """
                params_1.append(user_id)
                count_sql += ''' AND edit_log_id in('''
                if edit_log_ids:
                    for value in edit_log_ids:
                        count_sql += '''%s,'''
                        params_1.append(f'{value}')
                else:
                    count_sql += '''%s,'''
                    params_1.append("''")
                count_sql = count_sql[:-1] + ''') '''

                update_sql = """
                    UPDATE edit_notifications
                    SET is_read = 1
                    WHERE user_id = %s AND is_read = 0
                """
                params_2.append(user_id)
                update_sql += ''' AND edit_log_id in('''
                if edit_log_ids:
                    for value in edit_log_ids:
                        update_sql += '''%s,'''
                        params_2.append(f'{value}')
                else:
                    update_sql += '''%s,'''
                    params_2.append("''")
                update_sql = update_sql[:-1] + ''') '''
            else:
                count_sql = """
                    SELECT COUNT(*) as count
                    FROM edit_notifications
                    WHERE user_id = %s AND is_read = 0
                """
                
                update_sql = """
                    UPDATE edit_notifications
                    SET is_read = 1
                    WHERE user_id = %s AND is_read = 0
                """
            
                params_1.append(user_id)
                params_2.append(user_id)
            
            count = 0
            
            with db.get_cursor() as cursor:
                cursor.execute(count_sql, params_1)
                result = cursor.fetchone()
                count = result['count'] if result else 0
                
                if count > 0:
                    cursor.execute(update_sql, params_2)
                
            return count
        except Exception as e:
            flash(f"Error marking edit notifications as read: {e}", "danger")
            return 0
    
    @staticmethod
    def create_notification(user_id, edit_log_id):
        """
        Create a new edit notification.
        
        Args:
            user_id: The ID of the user to notify
            edit_log_id: The ID of the edit log
            
        Returns:
            The ID of the created notification
        """
        try:
            str_sql = """
                INSERT INTO edit_notifications
                (user_id, edit_log_id, is_read, created_at)
                VALUES (%s, %s, 0, NOW())
            """
            params = [user_id, edit_log_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                db.connect().commit()
                return cursor.lastrowid
        except Exception as e:
            flash(f"Error creating edit notification: {e}", "danger")
            return 0