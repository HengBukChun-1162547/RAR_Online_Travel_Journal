from flask import flash
from app import db

class FollowRepository:
    @staticmethod
    def view_follow_user(follower_id, followed_id):
        """view the follow user in the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''SELECT * FROM followed_users WHERE follower_id = %s AND followed_id = %s;''', (follower_id, followed_id))
                result = cursor.fetchone()
                if result:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to view follow user! ' + str(e), 'error')
            return False

    @staticmethod
    def create_follow_user(follower_id, followed_id):
        """create the follow user in the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''INSERT INTO followed_users (follower_id, followed_id) VALUES (%s, %s);''', (follower_id, followed_id))
                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to follow user! ' + str(e), 'error')
            return False

    @staticmethod
    def delete_follow_user(follower_id, followed_id):
        """delete the follow user in the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''DELETE FROM followed_users WHERE follower_id = %s AND followed_id = %s;''', (follower_id, followed_id))
                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to unfollow user! ' + str(e), 'error')
            return False

    @staticmethod
    def view_follow_journey(follower_id, journey_id):
        """view the follow journey in the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''SELECT * FROM followed_journeys WHERE follower_id = %s AND journey_id = %s;''', (follower_id, journey_id))
                result = cursor.fetchone()
                if result:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to view follow journey! ' + str(e), 'error')
            return False

    @staticmethod
    def create_follow_journey(follower_id, journey_id):
        """create the follow journey in the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''INSERT INTO followed_journeys (follower_id, journey_id) VALUES (%s, %s);''', (follower_id, journey_id))
                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to follow journey! ' + str(e), 'error')
            return False

    @staticmethod
    def delete_follow_journey(follower_id, journey_id):
        """delete the follow journey in the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''DELETE FROM followed_journeys WHERE follower_id = %s AND journey_id = %s;''', (follower_id, journey_id))
                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to unfollow journey! ' + str(e), 'error')
            return False