from flask import flash
from app import db

class GamificationRepository:
    """Repository class for gamification"""
        
    @staticmethod
    def get_achievement_types(achievement_type_id=None):
        """Get all achievement types"""
        
        try:
            str_sql = """
                        SELECT * FROM achievement_types
                        WHERE 1=1
                    """
            params = []
            if achievement_type_id:
                str_sql += " AND achievement_type_id = %s"
                params.append(achievement_type_id)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall() if achievement_type_id is None else cursor.fetchone()
        except Exception as e:
            flash(f"Error retrieving from getting details from achievement_types table: {e}", 'error')
            return None
    
    @staticmethod
    def get_user_achievement(user_id):
        """Get user's achievements"""
        try:
            str_sql = """
                SELECT achievement_type_id
                FROM user_achievements 
                WHERE user_id = %s
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id,))
                results = cursor.fetchall()
                return [result['achievement_type_id'] for result in results if 'achievement_type_id' in result]
        except Exception as e:
            flash(f"Error retrieving user achievements: {e}", 'error')
            return None

    @staticmethod
    def get_user_achievements_with_progress(user_id):
        """Get user's achievements and progress data"""
        try:
            str_sql = """
                SELECT 
                    at.achievement_type_id,
                    at.title,
                    at.description,
                    at.points,
                    at.icon_path,
                    at.is_premium,
                    ua.unlocked_at,
                    ap.achievement_progress_id,
                    COALESCE(ap.current_value, 0) as current_value,
                    COALESCE(ap.target_value, 0) as target_value,
                    ap.updated_at as progress_updated_at
                FROM achievement_types at
                LEFT JOIN user_achievements ua ON at.achievement_type_id = ua.achievement_type_id 
                    AND ua.user_id = %s
                LEFT JOIN achievement_progress ap ON at.achievement_type_id = ap.achievement_type_id 
                    AND ap.user_id = %s
                ORDER BY at.created_at ASC
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id, user_id))
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving user achievements with progress: {e}", 'error')
            return None 
        
    @staticmethod
    def get_user_achievement_progress(user_id, achievement_type_id):
        """Get user's achievement progress"""
        try:
            str_sql = """
                SELECT 
                    ap.achievement_progress_id,
                    COALESCE(ap.current_value, 0) as current_value,
                    COALESCE(ap.target_value, 0) as target_value,
                    ap.updated_at as progress_updated_at
                FROM achievement_progress ap
                WHERE ap.user_id = %s AND ap.achievement_type_id = %s
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id, achievement_type_id))
                return cursor.fetchone()
        except Exception as e:
            flash(f"Error retrieving user achievement progress: {e}", 'error')
            return None
        
    @staticmethod
    def create_user_achievement_progress(user_id, achievement_type_id, current_value, target_value):
        """Create new user achievement progress"""
        try:
            str_sql = """
                INSERT INTO achievement_progress (user_id, achievement_type_id, current_value, target_value)
                VALUES (%s, %s, %s, %s)
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id, achievement_type_id, current_value, target_value))
                return cursor.lastrowid
        except Exception as e:
            flash(f"Error creating user achievement progress: {e}", 'error')
            return None
        
    @staticmethod
    def update_user_achievement_progress(user_id, achievement_type_id, current_value):
        """Update existing user achievement progress"""
        try:
            str_sql = """
                UPDATE achievement_progress
                SET current_value = %s
                WHERE user_id = %s AND achievement_type_id = %s
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (current_value, user_id, achievement_type_id))
                return cursor.rowcount
        except Exception as e:
            flash(f"Error updating user achievement progress: {e}", 'error')
            return None
        
    @staticmethod
    def create_user_achievement(user_id, achievement_type_id):
        """Create new user achievement"""
        try:
            str_sql = """
                INSERT INTO user_achievements (user_id, achievement_type_id)
                VALUES (%s, %s)
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id, achievement_type_id))
                return cursor.lastrowid
        except Exception as e:
            flash(f"Error creating user achievement: {e}", 'error')
            return None
        
    @staticmethod
    def create_journey_view(user_id, journey_id, journey_status):
        """Create a new journey event view"""
        try:
            params = []
            str_sql = """
                SELECT * FROM journey_views
                WHERE user_id = %s AND journey_id = %s
                """
            params.append(user_id)
            params.append(journey_id)
            
            str_sql2 = """
                INSERT INTO journey_views (user_id, journey_id, journey_status)
                VALUES (%s, %s, %s)
                """
            params2 = [user_id, journey_id, journey_status]

            str_sql3 = """
                UPDATE journey_views
                SET journey_status = %s
                WHERE user_id = %s AND journey_id = %s
                """
            params3 = [journey_status, user_id, journey_id]

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                result = cursor.fetchone()
                if result:
                    if journey_status != result['journey_status']:
                        # Update the status if it has changed
                        cursor.execute(str_sql3, params3)
                        return cursor.lastrowid
                    else:
                        return None  # View already exists
                else:
                    cursor.execute(str_sql2, params2)
                    return cursor.lastrowid
        except Exception as e:
            flash(f"Error creating journey event view: {e}", 'error')
            return None
        
    @staticmethod
    def get_journey_views_first_user(user_id=None, status=None):
        """Get journey views for a user"""
        try:
            params = []
            str_sql = """
                SELECT jv.view_id, jv.user_id, jv.journey_id, jv.journey_status, jv.viewed_at, j.user_id as journey_owner_id
                FROM journey_views jv
                LEFT JOIN journeys j ON jv.journey_id = j.journey_id
                WHERE 1=1
                AND jv.journey_status in ('published','public')
                AND jv.user_id != j.user_id
                AND jv.viewed_at = (
                    SELECT MIN(jv2.viewed_at)
                    FROM journey_views jv2
                    LEFT JOIN journeys j2 ON jv2.journey_id = j2.journey_id
                    WHERE jv2.journey_id = jv.journey_id
                    AND jv2.journey_status in ('published','public')
                    AND jv2.user_id != j2.user_id
                )
                AND jv.user_id = %s
                """
            params.append(user_id)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving journey views: {e}", 'error')
            return None
        
    @staticmethod
    def get_support_requests(user_id):
        """Get support requests for a user"""
        try:
            str_sql = """
                SELECT * FROM support_requests
                WHERE user_id = %s
                ORDER BY created_at DESC;
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving support requests: {e}", 'error')
            return None
    
    @staticmethod
    def get_support_comments(user_id):
        """Get support comments for a user"""
        try:
            str_sql = """
                SELECT * FROM support_comments
                WHERE user_id = %s
                ORDER BY created_at DESC;
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving support comments: {e}", 'error')
            return None
        
    @staticmethod
    def get_followed_journeys(user_id):
        """Get followed journeys for a user"""
        try:
            str_sql = """
                SELECT * FROM followed_journeys
                WHERE follower_id = %s
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving followed journeys: {e}", 'error')
            return None
        
    @staticmethod
    def get_followed_users(user_id):
        """Get followed users for a user"""
        try:
            str_sql = """
                SELECT * FROM followed_users
                WHERE follower_id = %s
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving followed users: {e}", 'error')
            return None
        
    @staticmethod
    def get_edit_notifications(user_id):
        """Get edit logs read notifications for a user"""
        try:
            str_sql = """
                SELECT * FROM edit_notifications
                WHERE user_id = %s
                """
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving edit logs: {e}", 'error')
            return None
        
    @staticmethod
    def get_top_achievers_details(limit):
        """ get top achievers details """
        try:
            str_sql = """
                SELECT DENSE_RANK() OVER (ORDER BY COUNT(ua.user_achievement_id) DESC) AS ranks,u.username, u.user_id,
                u.first_name, u.last_name, u.profile_image,
                COUNT(ua.user_achievement_id) AS achievements,
                MAX(ua.unlocked_at) AS completed_at
                FROM users u
                LEFT JOIN user_achievements ua ON u.user_id = ua.user_id
                GROUP BY u.user_id, u.username
                ORDER BY ranks, completed_at ASC
                LIMIT %s;
                    """
            params = [limit]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving top achievers details: {e}", 'error')
            return None
    
    @staticmethod
    def get_recently_achieved_details(limit):
        """ get recently achieved details """
        try:
            str_sql = """
                    SELECT u.user_id, u.username, at.title AS achievement_title, at.description, at.icon_path, ua.unlocked_at
                    FROM users u
                    INNER JOIN user_achievements ua ON u.user_id = ua.user_id
                    INNER JOIN achievement_types at ON ua.achievement_type_id = at.achievement_type_id
                    ORDER BY ua.unlocked_at DESC
                    LIMIT %s;
                    """
            params = [limit]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving recently achieved details: {e}", 'error')
            return None
        