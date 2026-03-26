from flask import flash
from app import db

class EventRepository:
    @staticmethod
    def get_events(user_id=None):
        """get the events from the database"""
        try:
            str_sql = '''select distinct e.journey_id, l.name
                            from events e
                            left join journeys j on e.journey_id = j.journey_id
                            inner join locations l on e.location_id = l.location_id
                            where 1 = 1
                        '''
            params = []
            if user_id:
                str_sql += ''' AND j.user_id = %s'''
                params.append(user_id)

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                events = cursor.fetchall()
        except Exception as e:
            flash('Failed to get events! ' + e, 'error')
        return events
    
    @staticmethod
    def get_event_details(event_id=None, user_id=None):
        """get the event details from the database"""
        try:
            str_sql = '''
                        SELECT e.*, j.user_id as journey_owner_id, j.journey_id, j.status, j.hidden, j.title as journey_title
                        FROM events e
                        JOIN journeys j ON e.journey_id = j.journey_id
                        WHERE 1 = 1
                    '''
            params = []
            if event_id:
                str_sql += ''' AND e.event_id = %s'''
                params.append(event_id)
            if user_id:
                str_sql += ''' AND e.user_id = %s'''
                params.append(user_id)
                str_sql += ''' ORDER BY e.start_date DESC;'''

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone() if event_id else cursor.fetchall()
        except Exception as e:
            flash('Failed to get event details! ' + e, 'error')
            return None
        
    @staticmethod
    def get_event_locaiton_details(event_id):
        """get the event location details from the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''SELECT e.*, j.title as journey_title, j.journey_id, j.user_id as journey_owner_id,
                                    j.status, r.role_name, j.hidden, l.name as location_name, u.username as creator_name, updater.username as updater_name
                                    FROM events e
                                    JOIN journeys j ON e.journey_id = j.journey_id
                                    JOIN locations l ON e.location_id = l.location_id
                                    JOIN users u ON e.user_id = u.user_id
                                    JOIN roles r ON u.role_id = r.role_id
                                    LEFT JOIN users updater ON e.update_by = updater.user_id
                                    WHERE e.event_id = %s''', (event_id,))
                return cursor.fetchone()
        except Exception as e:
            flash('Failed to get event location details! ' + e, 'error')
            return None
    
    @staticmethod
    def get_event_images(event_id):
        """Get all image filenames or URLs for a specific event."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''
                    SELECT image_id, image_path  -- replace with actual column name
                    FROM event_images      -- replace with your actual table name
                    WHERE event_id = %s
                    ORDER BY image_id ASC  -- optional: order by upload or ID
                ''', (event_id,))
                results = cursor.fetchall()
                return results
        except Exception as e:
            flash('Failed to get event images! ' + str(e), 'error')
            return []
        
    @staticmethod
    def get_event_list_details(journey_id):
        """get the event list details from the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''SELECT e.event_id, e.journey_id, e.user_id, e.user_id as journey_owner_id,
                                    e.location_id, e.title, e.start_date, e.create_time, u.username AS created_by, l.name AS location, 
                                        updater.username as updater_name, e.update_time FROM events e
                                    LEFT JOIN locations l ON e.location_id = l.location_id 
                                    LEFT JOIN users u ON e.user_id = u.user_id 
                                    LEFT JOIN users updater ON e.update_by = updater.user_id
                                    WHERE journey_id = %s ORDER BY start_date ASC;''', (journey_id,))
                return cursor.fetchall()
        except Exception as e:
            flash('Failed to get event list details! ' + e, 'error')
            return None

    @staticmethod
    def add_event(event_data):
        """add an event to the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''INSERT INTO events 
                                (journey_id, user_id, location_id, title, description, 
                                    start_date, end_date, create_time, update_by)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)''', 
                               (event_data['journey_id'], event_data['user_id'], event_data['location_id'], event_data['title'], event_data['description'], event_data['start_date'], event_data['end_date'], event_data['update_by']))
                return cursor.lastrowid
        except Exception as e:
            flash('Failed to add event! ' + e, 'error')
            return -1

    @staticmethod
    def update_event_data(event_id, isStaff, event_data):
        """update an event in the database"""
        params=[]
        try:
            if isStaff:
                str_sql = ''' UPDATE events SET
                                location_id = %s, title = %s, description = %s, 
                                update_by = %s, update_time = NOW()
                                WHERE event_id = %s'''
                params.append(event_data['location_id'])
                params.append(event_data['title'])
                params.append(event_data['description'])
                params.append(event_data['update_by'])
                params.append(event_id)
            else:
                str_sql = ''' UPDATE events SET
                                location_id = %s, title = %s, description = %s, 
                                start_date = %s, end_date = NULL, update_by = %s, update_time = NOW()
                                WHERE event_id = %s'''
                params.append(event_data['location_id'])
                params.append(event_data['title'])
                params.append(event_data['description'])
                params.append(event_data['start_date'])
                params.append(event_data['update_by'])
                params.append(event_id)
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.rowcount
        except Exception as e:
            flash('Failed to update event! ' + e, 'error')
            return -1

    @staticmethod
    def update_event(event_id, isNew, image_path=None, update_by=None, image_path_to_delete=None, image_id=None):
        try:
            with db.get_cursor() as cursor:
                if isNew and image_path:
                    cursor.execute(
                        '''INSERT INTO event_images (event_id, image_path) VALUES (%s, %s)''',
                        (event_id, image_path))

                elif not isNew and update_by and image_path == "NULL" and image_path_to_delete:
                    cursor.execute(
                        '''DELETE FROM event_images WHERE event_id = %s AND image_path = %s''',
                        (event_id, image_path_to_delete))
                
                elif not isNew and update_by and image_id and image_path:
                # Update the image path for the given event_id
                    cursor.execute(
                        '''UPDATE event_images SET image_path = %s WHERE image_id = %s AND event_id = %s''',
                        (image_path, image_id, event_id))

                return cursor.rowcount
        except Exception as e:
            flash('Failed to update event! ' + str(e), 'error')
            return -1
        
    @staticmethod
    def delete_event(event_id):
        """delete an event from the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''DELETE FROM events WHERE event_id = %s''', (event_id,))
                return cursor.rowcount
        except Exception as e:
            flash('Failed to delete event! ' + e, 'error')
            return -1


class LocationRepository:
    @staticmethod
    def get_locations(name=None, location_id=None):
        """get the locations from the database"""
        try:
            str_sql = '''SELECT location_id, name FROM locations
                            WHERE 1 = 1''' 
            params = []

            if name:
                str_sql += ''' AND name = %s'''
                params.append(name)
            
            if location_id:
                str_sql += ''' AND location_id = %s'''
                params.append(location_id)
            
            str_sql += ''' ORDER BY name;'''

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                return cursor.fetchone() if len(params) == 1 else cursor.fetchall()
        except Exception as e:
            flash('Failed to get locations! ' + e, 'error')
            return None
        
    @staticmethod
    def add_location(name):
        """add a location to the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''INSERT INTO locations (name) VALUES (%s)''', (name,))
                return cursor.lastrowid
        except Exception as e:
            flash('Failed to add location! ' + e, 'error')
            return -1

    @staticmethod
    def get_all_locations(search_term=None):
        """Get all locations with usage counts, optionally filtered by search term"""
        with db.get_cursor() as cursor:
            query = """
                SELECT l.location_id, l.name, COUNT(e.event_id) as usage_count
                FROM locations l
                LEFT JOIN events e ON l.location_id = e.location_id
            """
            
            params = []
            if search_term:
                query += " WHERE l.name LIKE %s"
                params.append(f'%{search_term}%')
            
            query += " GROUP BY l.location_id, l.name ORDER BY l.name"
            
            cursor.execute(query, params)
            locations = cursor.fetchall()
            return locations
        
    @staticmethod
    def merge_locations(source_location_ids, target_location_id):
        """Merge multiple source locations into a target location and delete source locations"""
        if not source_location_ids or not target_location_id:
            return False, "Source locations and target location are required"
        
        try:
            with db.get_cursor() as cursor:     
                updated_events_count = 0
                deleted_locations_count = 0
                skipped_locations_count = 0
                
                # Update all events for each source location
                for source_id in source_location_ids:
                    if int(source_id) == int(target_location_id):
                        skipped_locations_count += 1
                        continue  # Skip if source and target are the same
                    
                    # Update all events using this source location
                    cursor.execute(
                        "UPDATE events SET location_id = %s WHERE location_id = %s",
                        (target_location_id, source_id)
                    )
                    updated_events_count += cursor.rowcount
                    
                    # Delete source location after updating events
                    cursor.execute("DELETE FROM locations WHERE location_id = %s", (source_id,))
                    deleted_locations_count += cursor.rowcount
                
                cursor.close()
                
                return True, {
                    "updated_events": updated_events_count,
                    "deleted_locations": deleted_locations_count,
                    "skipped_locations": skipped_locations_count
                }
        except Exception as e:
            # Autocommit enabled, no rollback needed
            return False, f"Error merging locations: {str(e)}"
        
    @staticmethod       
    def is_user_following_location(user_id, location_id):
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM followed_locations WHERE follower_id=%s AND location_id=%s",
                (user_id, location_id)
            )
            return cursor.fetchone() is not None

    @staticmethod
    def follow_location(user_id, location_id):
        try:
            with db.get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO followed_locations (follower_id, location_id) VALUES (%s, %s)",
                    (user_id, location_id)
                )
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def unfollow_location(user_id, location_id):
        with db.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM followed_locations WHERE follower_id=%s AND location_id=%s",
                (user_id, location_id)
            )
    @staticmethod
    def get_events_from_followed_locations(user_id):
        with db.get_cursor() as cursor:
            cursor.execute('''
                SELECT e.* FROM events e
                JOIN followed_locations f ON e.location_id = f.location_id
                WHERE f.follower_id = %s
                ORDER BY e.update_by DESC, e.start_date DESC
            ''', (user_id,))
            return cursor.fetchall()