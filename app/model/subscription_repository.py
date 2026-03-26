# from flask import flash
from app import db

class SubscriptionRepository:
    @staticmethod
    def get_subscription_plan(subscription=None, subscription_plan_id=None, subscription_type=None):
        """ Get subscription plan."""
        try:
            str_sql = """SELECT subscription_plan_id, name, duration_months, discount_percent, price_excl_gst, gst_percentage, subscription_type
                            FROM subscription_plans
                            where 1=1
                        """
            params = []
            if subscription_plan_id:
                str_sql += " AND subscription_plan_id = %s"
                params.append(subscription_plan_id)
            elif subscription_type:
                str_sql += " AND subscription_type = %s"
                params.append(subscription_type)
            elif subscription:
                str_sql += " AND subscription_type in('Trial','Purchased')"
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone() if subscription_plan_id else cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving subscription plans: {e}")
            return None
    
    @staticmethod
    def get_newest_subscription(user_id, limit=None):
        """ Get the most recent subscription for a user."""
        try:
            str_sql = """
                        SELECT * FROM active_subscriptions 
                        WHERE user_id = %s 
                        and is_active = 1
                        ORDER BY expiry_date DESC 
                    """
            params = [user_id]

            if limit:
                str_sql += " LIMIT %s"
                params.append(limit)

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                if limit and limit == 1:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving the latest subscription: {e}")
            return None

    @staticmethod
    def create_subscription(user_id, subscription_type, subscription_plan_id, start_date, expiry_date, created_by, note):
        """ Create a new subscription."""
        try:
            str_sql = """INSERT INTO subscriptions (user_id, subscription_type, subscription_plan_id, start_date, expiry_date, created_by, note)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            params = (user_id, subscription_type, subscription_plan_id, start_date, expiry_date, created_by, note)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating subscription: {e}")
            return None
        
    @staticmethod
    def get_free_trial_subscription(user_id):
        """ Get the free trial subscription for a user."""
        try:
            str_sql = """
                        SELECT user_id, trial_used, subscription_id FROM free_trial_usage 
                        WHERE user_id = %s
                    """
            params = [user_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone()
        except Exception as e:
            print(f"Error retrieving free trial subscription: {e}")
            return None
        
        finally:
            db.close_db()
        
    @staticmethod
    def get_expired_subscription_details():
        """ Get expired subscription details"""
        try:
            str_sql = """
                        SELECT user_id, 
                        MAX(expiry_date) AS latest_expiry,
                        DATEDIFF(MAX(expiry_date), NOW()) AS days_remaining
                        FROM subscriptions
                        GROUP BY user_id;
                      """
            params = []
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving the first subscribed date: {e}")
            return None
    
        finally:
            db.close_db()

    @staticmethod
    def get_all_subscription_details(user_id):
        """ Get all subscription details including start date, end date, subscription type, payment details"""
        try:
            str_sql = """
                        SELECT s.subscription_id, s.user_id, s.subscription_type, s.start_date, s.expiry_date,
                        sp.name AS plan_name, sp.duration_months,
                        p.payment_date, p.payment_amount
                        FROM subscriptions s
                        INNER JOIN subscription_plans sp 
                        ON s.subscription_plan_id = sp.subscription_plan_id
                        LEFT JOIN payments p 
                        ON s.subscription_id = p.subscription_id
                        WHERE s.user_id =  %s
                        ORDER BY s.expiry_date DESC
                    """
            params = [user_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving all active subscriptions: {e}")
            return None
        
    @staticmethod
    def get_all_subscription_transaction_details(user_id):
        """ Get all subscription transaction details"""
        try:
            str_sql = """
                        SELECT 
                            s.subscription_id,
                            sp.name AS plan_name,
                            s.subscription_type,
                            s.start_date,
                            s.expiry_date,
                            p.*
                        FROM subscriptions s
                        LEFT JOIN payments p ON s.subscription_id = p.subscription_id
                        LEFT JOIN subscription_plans sp ON s.subscription_plan_id = sp.subscription_plan_id
                        WHERE s.user_id = %s
                        ORDER BY s.expiry_date DESC;
                    """
            params = [user_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving all subscription payment details: {e}")
            return None
        
    @staticmethod
    def get_invoice_details(payment_id):
        """ Get invoice details"""
        try:
            str_sql = """
                        SELECT 
                            s.subscription_id,
                            s.user_id,
                            sp.name AS plan_name,
                            s.subscription_type,
                            s.start_date,
                            s.expiry_date,
                            sp.price_excl_gst,
                            (YEAR(s.expiry_date) - YEAR(s.start_date)) * 12 + (MONTH(s.expiry_date) - MONTH(s.start_date)) AS duration_months,
                            p.*
                        FROM subscriptions s
                        LEFT JOIN payments p ON s.subscription_id = p.subscription_id
                        LEFT JOIN subscription_plans sp ON s.subscription_plan_id = sp.subscription_plan_id
                        WHERE p.payment_id = %s
                    """
            params = [payment_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving invoice details: {e}")
            return None
    
    @staticmethod
    def get_first_subscribed_date(user_id):
        """ Get the first subscribed date"""
        try:
            str_sql = """
                        SELECT start_date FROM subscriptions
                        Where user_id = %s
                        Order by start_date ASC
                        LIMIT 1;
                    """
            params = [user_id]
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone()
        except Exception as e:
            print(f"Error retrieving the first subscribed date: {e}")
            return None

        
    def create_free_trial_subscription(user_id, trial_used, subscription_id):
        """ Create a new free trial subscription."""
        try:
            str_sql = """INSERT INTO free_trial_usage (user_id, trial_used, subscription_id)
                        VALUES (%s, %s, %s)"""
            params = (user_id, trial_used, subscription_id)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount
        except Exception as e:
            print(f"Error creating free trial subscription: {e}")
            return None

    @staticmethod
    def update_subscription_expiry_date(subscription_id, new_expiry_date):
        """ Update the expiry date of a subscription."""
        try:
            str_sql = """UPDATE subscriptions 
                        SET expiry_date = %s 
                        WHERE subscription_id = %s"""
            params = (new_expiry_date, subscription_id)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount
        except Exception as e:
            print(f"Error updating subscription expiry date: {e}")
            return None


class PaymentRepository:
    @staticmethod
    def create_payment(subscription_id, payment_amount, card_number, card_cvv, card_expiry_date, card_holder, card_type, billing_country, address1, address2, city, state, postal):
        """ Create a new payment."""
        try:
            str_sql = """INSERT INTO payments (subscription_id, payment_amount, card_number, card_cvv, card_expiry_date, 
                        card_holder, card_type, billing_country, address1, address2, city, state, postal)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            params = []
            params.append(subscription_id)
            params.append(payment_amount)
            params.append(card_number)
            params.append(card_cvv)
            params.append(card_expiry_date)
            params.append(card_holder)
            params.append(card_type)
            params.append(billing_country)
            params.append(address1)
            params.append(address2) if address2 else params.append(None)
            params.append(city)
            params.append(state)
            params.append(postal)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating payment: {e}")
            return None