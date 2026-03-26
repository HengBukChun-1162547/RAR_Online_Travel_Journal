from flask import flash
from app import db

class EditLogRepository:
    @staticmethod
    def create_edit_log(journey_id, event_id, editor_id, edit_reason, summary):
        """
        Create a new edit log entry in the database.
        """
        try:
            str_sql = """
                        INSERT INTO edit_logs (journey_id, event_id, editor_id, edit_reason, summary)
                        VALUES (%s, %s, %s, %s, %s)
                        """
            params = [journey_id, event_id, editor_id, edit_reason, summary]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.lastrowid
        except Exception as e:
            flash(f"Error creating edit log: {e}", "danger")

    @staticmethod
    def get_edit_logs(journey_id, event_id):
        """
        Retrieve all edit logs for a specific journey.
        """
        try:
            str_sql = """
                        SELECT u.username as editor_username, el.edit_log_id, el.editor_id, el.edited_at, el.edit_reason, el.summary 
                        FROM edit_logs el 
                        LEFT JOIN users u ON el.editor_id = u.user_id
                        WHERE 1=1 
                        """
            params = []
            if journey_id:
                str_sql += " AND journey_id = %s AND event_id IS NULL"
                params.append(journey_id)
            
            if event_id:
                str_sql += " AND event_id = %s"
                params.append(event_id)

            str_sql += " ORDER BY edited_at DESC"
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving edit logs: {e}", "danger")

    @staticmethod
    def get_edit_log_by_log_id(edit_log_id):
        """
        Retrieve a specific edit log by its ID.
        """
        try:
            str_sql = """
                        SELECT u.username as editor_username, el.edit_log_id, el.editor_id, el.edited_at, el.edit_reason, el.summary, el.journey_id, el.event_id 
                        FROM edit_logs el 
                        LEFT JOIN users u ON el.editor_id = u.user_id
                        WHERE edit_log_id = %s
                        """
            params = [edit_log_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone()
        except Exception as e:
            flash(f"Error retrieving edit log by ID: {e}", "danger")

    @staticmethod
    def get_edit_logs_by_journey_user(user_id, journey_id=None, event_id=None):
        """
        Retrieve all edit logs for a specific user across all journeys.
        """
        try:
            str_sql = """
                        SELECT u.username as editor_username, el.edit_log_id, el.editor_id, el.edited_at, el.edit_reason, el.summary, el.journey_id, el.event_id, j.user_id 
                        FROM edit_logs el 
                        LEFT JOIN journeys j ON el.journey_id = j.journey_id
                        LEFT JOIN users u ON el.editor_id = u.user_id
                        WHERE j.user_id = %s
                        """
            params = [user_id]
            if journey_id:
                str_sql += " AND el.journey_id = %s"
                params.append(journey_id)
            if event_id:
                str_sql += " AND el.event_id = %s"
                params.append(event_id)
            str_sql += " ORDER BY el.edited_at DESC"
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving edit logs by user: {e}", "danger")

    @staticmethod
    def create_edit_notification(user_id, edit_log_id):
        """
        Create a new edit notification entry in the database.
        """
        try:
            str_sql = """
                        INSERT INTO edit_notifications (user_id, edit_log_id)
                        VALUES (%s, %s)
                        """
            params = [user_id, edit_log_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.lastrowid
        except Exception as e:
            flash(f"Error creating edit notification: {e}", "danger")