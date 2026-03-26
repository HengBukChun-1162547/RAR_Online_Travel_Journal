from flask import flash
from app import db

class AnnouncementRepository:
    """Repository class for handling announcement-related database operations."""
    
    @staticmethod
    def get_announcement(announcement_id=None, user_id=None, search_term=None, limit=None):
        try:
            str_sql = """
                SELECT a.announcement_id, a.user_id, a.title, a.description, 
                       a.create_time, a.update_by, a.update_time,
                       u1.username as creator_name, u2.username as updater_name
                FROM announcements a
                LEFT JOIN users u1 ON a.user_id = u1.user_id
                LEFT JOIN users u2 ON a.update_by = u2.user_id
            """
            params = []

            if announcement_id:
                str_sql += " WHERE a.announcement_id = %s"
                params.append(announcement_id)
            elif user_id:
                str_sql += " WHERE a.user_id = %s"
                params.append(user_id)
            elif search_term:
                str_sql += " WHERE a.title LIKE %s OR a.description LIKE %s"
                search_pattern = f"%{search_term}%"
                params.append(search_pattern)
                params.append(search_pattern)
            
            # Add order by newest first
            str_sql += " ORDER BY a.create_time DESC"
            
            # Add limit if specified
            if limit and not announcement_id:
                str_sql += " LIMIT %s"
                params.append(limit)

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone() if announcement_id else cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving announcement data: {e}", "danger")
            return None
    
    @staticmethod
    def get_unread_announcements(unread_ids, limit=None):
        try:
            str_sql = """
                SELECT a.announcement_id, a.title, a.create_time, u.username as creator_name
                FROM announcements a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.announcement_id IN ({})
                ORDER BY a.create_time DESC
                """.format(','.join(['%s'] * len(unread_ids)))
            
            params = unread_ids.copy()
            
            # Add limit if specified
            if limit:
                str_sql += " LIMIT %s"
                params.append(limit)

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving unread announcements: {e}", "danger")
            return None

    @staticmethod
    def create_announcement(user_id, title, description):
        try:
            str_sql = """
                INSERT INTO announcements (user_id, title, description)
                VALUES (%s, %s, %s)
            """
            params = [user_id, title, description]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.lastrowid
        except Exception as e:
            flash(f"Error creating announcement: {e}", "danger")
            return -1
    
    @staticmethod
    def update_announcement(announcement_id, update_by, title=None, description=None):
        try:
            update_parts = []
            params = []
            
            if title is not None:
                update_parts.append("title = %s")
                params.append(title)
            
            if description is not None:
                update_parts.append("description = %s")
                params.append(description)
            
            # Always update the update_by field
            update_parts.append("update_by = %s")
            params.append(update_by)
            
            # If no fields to update, return
            if not update_parts:
                return False
                
            str_sql = f"""
                UPDATE announcements 
                SET {', '.join(update_parts)}
                WHERE announcement_id = %s
            """
            params.append(announcement_id)
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount > 0
        except Exception as e:
            flash(f"Error updating announcement: {e}", "danger")
            return False
    
    @staticmethod
    def delete_announcement(announcement_id):
        try:
            str_sql = "DELETE FROM announcements WHERE announcement_id = %s"
            params = [announcement_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount > 0
        except Exception as e:
            flash(f"Error deleting announcement: {e}", "danger")
            return False
    
    @staticmethod
    def get_unread_announcements_count(user_id):
        try:
            str_sql = """
                SELECT COUNT(a.announcement_id) AS unread_count
                FROM announcements a
                LEFT JOIN announcement_reads ar ON a.announcement_id = ar.announcement_id AND ar.user_id = %s
                WHERE ar.announcement_read_id IS NULL
            """
            params = [user_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                result = cursor.fetchone()
                return result['unread_count'] if result else 0
        except Exception as e:
            flash(f"Error counting unread announcements: {e}", "danger")
            return 0
    
    @staticmethod
    def get_unread_announcement_ids(user_id):
        """
        Get the IDs of unread announcements for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            list: List of unread announcement IDs
        """
        try:
            str_sql = """
                SELECT a.announcement_id
                FROM announcements a
                LEFT JOIN announcement_reads ar ON a.announcement_id = ar.announcement_id AND ar.user_id = %s
                WHERE ar.announcement_read_id IS NULL
            """
            params = [user_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                results = cursor.fetchall()
                return [row['announcement_id'] for row in results]
        except Exception as e:
            flash(f"Error getting unread announcements: {e}", "danger")
            return []

    @staticmethod
    def mark_announcement_as_read(user_id, announcement_id):
        try:
            # First check if already marked as read
            str_check = """
                SELECT announcement_read_id FROM announcement_reads
                WHERE user_id = %s AND announcement_id = %s
            """
            
            str_insert = """
                INSERT INTO announcement_reads (user_id, announcement_id)
                VALUES (%s, %s)
            """
            params = [user_id, announcement_id]
            
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
    def mark_all_announcements_as_read(user_id):
        try:
            str_sql = """
                INSERT INTO announcement_reads (user_id, announcement_id)
                SELECT %s, a.announcement_id
                FROM announcements a
                LEFT JOIN announcement_reads ar ON a.announcement_id = ar.announcement_id AND ar.user_id = %s
                WHERE ar.announcement_read_id IS NULL
            """
            params = [user_id, user_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount
        except Exception as e:
            flash(f"Error marking all announcements as read: {e}", "danger")
            return 0