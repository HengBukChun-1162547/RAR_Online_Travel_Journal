from flask import flash
from app import db

class AuthorityRepository:
    @staticmethod
    def get_user_permissions(user_id):
        try:
            str_sql = """
                        SELECT DISTINCT p.permission_name
                        FROM users u
                        JOIN role_permissions rp ON u.role_id = rp.role_id
                        JOIN permissions p ON rp.permission_id = p.permission_id
                        WHERE u.user_id = %s
                        """
            params = [user_id]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                results = cursor.fetchall()
                return [result['permission_name'] for result in results if 'permission_name' in result]
        except Exception as e:
            flash(f"Error getting user permission: {e}", "danger")
            return None
        
    @staticmethod
    def get_role_id(role_name):
        try:
            str_sql = """
                        SELECT role_id
                        FROM roles
                        WHERE role_name = %s
                        """
            params = [role_name]
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                result = cursor.fetchone()
                return result['role_id'] if result else None
        except Exception as e:
            flash(f"Error getting role name: {e}", "danger")
            return None