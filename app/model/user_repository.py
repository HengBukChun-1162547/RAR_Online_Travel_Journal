from flask import flash
from app import db
from app.model.authority_repository import AuthorityRepository

class UserRepository:
    """ get_user function retrieves user information from the database."""
    @staticmethod
    def get_user(user_id=None, email=None, username=None, search_user=None):
        try: 
            str_sql = """SELECT u.user_id, u.username, u.password_hash, u.email, u.first_name, u.last_name,
                            u.location, u.profile_image, u.description, r.role_name as role, u.status 
                            FROM users u
                            LEFT JOIN roles r ON u.role_id = r.role_id"""
            params = []

            if user_id:
                str_sql += " WHERE u.user_id = %s"
                params.append(user_id)
            elif email:
                str_sql += " WHERE u.email = %s"
                params.append(email)
            elif username:
                str_sql += " WHERE u.username = %s"
                params.append(username)
            elif search_user:
                str_sql += " WHERE u.username LIKE %s OR u.first_name LIKE %s OR u.last_name LIKE %s OR u.email LIKE %s"
                params.append(search_user)
                params.append(search_user)
                params.append(search_user)
                params.append(search_user)
            else:
                str_sql += " ORDER BY u.username"

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone() if len(params) == 1 else cursor.fetchall()
        except Exception as e:
            flash(f"Error retrieving user data: {e}")
    
    """ Update user data in the database."""
    @staticmethod
    def update_user_data(user_id, update_data):
        try:
            str_sql = '''UPDATE users SET 
                        first_name = %s, last_name = %s, email = %s, 
                        location = %s, description = %s 
                        WHERE user_id = %s'''
            params = []
            params.append(update_data['first_name'])
            params.append(update_data['last_name'])
            params.append(update_data['email'])
            params.append(update_data['location']) if update_data['location'] else params.append(None)
            params.append(update_data['description']) if update_data['description'] else params.append(None)
            params.append(user_id)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount
        except Exception as e:
            flash(f"Error updating user data: {e}")
            return -1
        
    @staticmethod
    def update_user(user_id, role=None, status=None, image_path=None, password_hash=None):
        try:
            str_sql = ""
            params = []
            if role:
                role_id = AuthorityRepository.get_role_id(role)
                if role_id:
                    str_sql = "UPDATE users SET role_id = %s WHERE user_id = %s;"
                    params.append(role_id)
                    params.append(user_id)
                else:
                    flash(f"Role '{role}' does not exist.")
                    return -1
            if status:
                str_sql = "UPDATE users SET status = %s WHERE user_id = %s;"
                params.append(status)
                params.append(user_id)
                                                                                
            if image_path:
                if image_path == "NULL":
                    image_path = None
                    str_sql = "UPDATE users SET profile_image = %s WHERE user_id = %s;"
                    params.append(image_path)
                    params.append(user_id)
                else:
                    str_sql = "UPDATE users SET profile_image = %s WHERE user_id = %s;"
                    params.append(image_path)
                    params.append(user_id)
            
            if password_hash:
                str_sql = "UPDATE users SET password_hash = %s WHERE user_id = %s;"
                params.append(password_hash)
                params.append(user_id)
            
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount
        except Exception as e:
            flash(f"Error updating user: {e}")
            return -1

    @staticmethod
    def add_user(user_data):
        try:
            with db.get_cursor() as cursor:
                str_sql = '''INSERT INTO users (username, email, password_hash, first_name, last_name, location, role_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
                params = []
                params.append(user_data['username'])
                params.append(user_data['email'])
                params.append(user_data['password_hash'])
                params.append(user_data['first_name']) if user_data['first_name'] else params.append(None)
                params.append(user_data['last_name']) if user_data['last_name']  else params.append(None)
                params.append(user_data['location']) if user_data['location'] else params.append(None)
                params.append(user_data['role_id'])
                params.append(user_data['status'])
                cursor.execute(str_sql, params)
                return cursor.rowcount
        except Exception as e:
            flash(f"Error adding new user: {e}")
            return -1

    @staticmethod
    def get_active_subscription(user_id):
        """Get a user's current active subscription"""
        try:
            # Query user's current active subscription
            query = """
            SELECT s.subscription_id, s.user_id, s.subscription_type, s.subscription_plan_id, 
                s.start_date, s.expiry_date, s.created_by, s.note,
                sp.name AS plan_name, sp.duration_months
            FROM subscriptions s
            JOIN subscription_plans sp ON s.subscription_plan_id = sp.subscription_plan_id
            WHERE s.user_id = %s AND s.expiry_date > NOW()
            ORDER BY s.expiry_date DESC
            LIMIT 1
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return result  # Returns dictionary from cursor
                return None
        except Exception as e:
            flash(f"Error retrieving active subscription: {e}")
            return None

    @staticmethod
    def get_subscription_history(user_id):
        """Get a user's complete subscription history"""
        try:
            # Query all subscription records for the user
            query = """
            SELECT s.subscription_id, s.subscription_type, s.start_date, s.expiry_date, 
                s.created_by, s.note, sp.name AS plan_name, sp.duration_months,
                CASE 
                    WHEN s.expiry_date > NOW() THEN TRUE
                    ELSE FALSE
                END AS is_active,
                admin.username AS admin_name
            FROM subscriptions s
            JOIN subscription_plans sp ON s.subscription_plan_id = sp.subscription_plan_id
            LEFT JOIN users admin ON s.created_by = admin.user_id
            WHERE s.user_id = %s
            ORDER BY s.start_date DESC
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                return results  # Already returns a list of dictionaries
        except Exception as e:
            flash(f"Error retrieving subscription history: {e}")
            return []

    @staticmethod
    def get_subscription(subscription_id):
        """Get details for a specific subscription"""
        try:
            query = """
            SELECT s.subscription_id, s.user_id, s.subscription_type, s.subscription_plan_id,
                s.start_date, s.expiry_date, s.created_by, s.note,
                sp.name AS plan_name, sp.duration_months, sp.price_excl_gst, sp.gst_percentage,
                u.username, admin.username AS admin_name
            FROM subscriptions s
            JOIN subscription_plans sp ON s.subscription_plan_id = sp.subscription_plan_id
            JOIN users u ON s.user_id = u.user_id
            LEFT JOIN users admin ON s.created_by = admin.user_id
            WHERE s.subscription_id = %s
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, (subscription_id,))
                return cursor.fetchone()  # Already returns a dictionary
        except Exception as e:
            flash(f"Error retrieving subscription details: {e}")
            return None

    @staticmethod
    def get_payment(subscription_id):
        """Get payment details for a subscription"""
        try:
            query = """
            SELECT p.payment_id, p.payment_date, p.payment_method, 
                SUBSTRING(p.card_number, 1, 4) AS card_first_four,
                p.billing_country
            FROM payments p
            WHERE p.subscription_id = %s
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, (subscription_id,))
                return cursor.fetchone()  # Already returns a dictionary
        except Exception as e:
            flash(f"Error retrieving payment details: {e}")
            return None

    @staticmethod
    def create_gifted_subscription(user_id, admin_id, plan_id, duration_months, reason, current_status, remaining_days, expiry_date):
        """Create a subscription gifted by an admin"""
        try:
            # Calculate subscription start and end dates
            import datetime
            new_start_date = datetime.datetime.now()
            
            # If user has an existing subscription, add to it
            if remaining_days > 0:
                new_start_date = expiry_date + datetime.timedelta(days=1)
            # Calculate end date (in months, each month is 30 days)
            new_expiry_date = new_start_date + datetime.timedelta(days=duration_months * 30)
            
            # Insert subscription
            with db.get_cursor() as cursor:
                query = """
                INSERT INTO subscriptions (user_id, subscription_type, subscription_plan_id, start_date, expiry_date, created_by, note)
                VALUES (%s, 'Gifted', %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (user_id, plan_id, new_start_date, new_expiry_date, admin_id, reason))
                
            return True

        except Exception as e:
            flash(f"Error creating gifted subscription: {e}")
            return False