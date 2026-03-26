from flask import flash
from app import db

class SupportRepository:
    """Repository class for support request data operations"""
    
    @staticmethod
    def create_request(user_id, issue_type, summary, description, screenshot_path=None):
        """Create support requests"""
        try:
            # check user role
            is_premium = False
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT r.role_name 
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = %s
                """, [user_id])
                result = cursor.fetchone()
                if result:
                    role = result['role_name']
                    is_premium = role in ['premium', 'trial', 'editor', 'admin', 'support_tech']
            
            # create request
            priority = 'High' if is_premium else 'Normal'
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO support_requests 
                    (user_id, issue_type, summary, description, screenshot_path, priority)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [user_id, issue_type, summary, description, screenshot_path, priority])
                return cursor.lastrowid
        except Exception as e:
            flash(f"It fails to create request: {e}", "danger")
            return -1
    
    @staticmethod
    def get_user_requests(user_id=None, status=None, priority=None,issue_type=None):
        """Acquire all support requests"""
        try:
            query = """
                SELECT r.*, u.username as creator_name, a.username as assignee_name
                FROM support_requests r
                JOIN users u ON r.user_id = u.user_id
                LEFT JOIN users a ON r.assignee_id = a.user_id
                WHERE 1+1
            """
            params = []

            if user_id:
                query += " AND r.user_id = %s"
                params.append(user_id)
            
            if status:
                query += " AND r.status = %s"
                params.append(status)
            
            if priority:
                query += " AND r.priority = %s"
                params.append(priority)
            
            if issue_type:
                query += " AND r.issue_type = %s"
                params.append(issue_type)
                
            # Add custom ordering
            query += """
                ORDER BY 
                CASE 
                    WHEN r.status = 'Resolved' THEN 2
                    ELSE 1
                END,
                CASE r.priority
                    WHEN 'High' THEN 1
                    WHEN 'Normal' THEN 2
                    ELSE 3
                END,               
                r.created_at ASC """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            flash(f"It fails to acquire support requests: {e}", "danger")
            return []
    
    @staticmethod
    def get_request_details(request_id):
        """Acquire detail info for all support requests"""
        try:
            query = """
                SELECT r.*, u.username as creator_name, a.username as assignee_name
                FROM support_requests r
                JOIN users u ON r.user_id = u.user_id
                LEFT JOIN users a ON r.assignee_id = a.user_id
                WHERE r.request_id = %s
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, [request_id])
                return cursor.fetchone()
        except Exception as e:
            flash(f"It fails to acquire detail info for all support requests: {e}", "danger")
            return None
    
    @staticmethod
    def add_comment(request_id, user_id, comment):
        """Add comments for support requests"""
        try:
            query = """
                INSERT INTO support_comments
                (request_id, user_id, comment)
                VALUES (%s, %s, %s)
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, [request_id, user_id, comment])
                return cursor.lastrowid
        except Exception as e:
            flash(f"It fails to add comments for support requests: {e}", "danger")
            return -1
    
    @staticmethod
    def get_request_comments(request_id):
        """Get all comments for support requests"""
        try:
            query = """
                SELECT c.*, u.username
                FROM support_comments c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.request_id = %s
                ORDER BY c.created_at ASC
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, [request_id])
                return cursor.fetchall()
        except Exception as e:
            flash(f"It fails to get all comments for support requests: {e}", "danger")
            return []
    
    @staticmethod
    def update_request_status(request_id, status, assignee_id=None):
        """Update support request status"""
        try:
            # Add debug log
            print(f"Updating request {request_id} with status {status} and assignee_id {assignee_id}")
            
            # Build query
            if assignee_id is None:
                # When dropping a request, explicitly set assignee_id to NULL
                query = """
                    UPDATE support_requests 
                    SET status = %s, assignee_id = NULL
                    WHERE request_id = %s
                    """
                params = [status, request_id]
            else:
                # Take or update request
                query = """
                    UPDATE support_requests 
                    SET status = %s, assignee_id = %s
                    WHERE request_id = %s
                    """
                params = [status, assignee_id, request_id]
            
            # Execute query
            with db.get_cursor() as cursor:
                cursor.execute(query, params)
                
                # Get number of affected rows
                affected_rows = cursor.rowcount
                print(f"Affected rows: {affected_rows}")
                
                return affected_rows > 0
        except Exception as e:
            # Output detailed error information
            print(f"Error updating request status: {e}")
            flash(f"Error updating request status: {e}", "danger")
            return False

    @staticmethod
    def get_staff_users():
        """Get all staff users who can be assigned to requests"""
        try:
            query = """
                SELECT u.user_id, u.username, r.role_name
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE r.role_name IN ('admin', 'editor', 'support_tech')
                AND u.status = 'active'
                ORDER BY r.role_name, u.username
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            flash(f"Error getting staff users: {e}", "danger")
            return []

    @staticmethod
    def can_modify_request(request_id, user_id):
        """Check if user can modify the request (only assignee can modify)"""
        try:
            query = """
                SELECT assignee_id, status
                FROM support_requests
                WHERE request_id = %s
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, [request_id])
                result = cursor.fetchone()
                
                if not result:
                    return False
                
                # Only the assignee can modify the request
                # If request is not assigned, nobody can modify status (except for take/assign actions)
                return result['assignee_id'] == user_id if result['assignee_id'] else False
        except Exception as e:
            print(f"Error checking request modification permission: {e}")
            return False