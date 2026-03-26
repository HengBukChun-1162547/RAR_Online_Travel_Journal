from flask import flash, session
from app import db

class DepartureRepository:
    """Repository for handling Departure Board data operations"""
    
    @staticmethod
    def get_departure_board_events(user_id, filter_type=None, page=1, per_page=10):
        try:
            # Calculate pagination offset
            offset = (page - 1) * per_page
            
            with db.get_cursor() as cursor:
                # First check if user has any followed content
                cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM followed_journeys WHERE follower_id = %s) as journey_count,
                    (SELECT COUNT(*) FROM followed_users WHERE follower_id = %s) as user_count,
                    (SELECT COUNT(*) FROM followed_locations WHERE follower_id = %s) as location_count
                """, [user_id, user_id, user_id])
                
                counts = cursor.fetchone()
                has_followed_journeys = counts['journey_count'] > 0
                has_followed_users = counts['user_count'] > 0
                has_followed_locations = counts['location_count'] > 0
                
                # If no followed content, return early
                if not (has_followed_journeys or has_followed_users or has_followed_locations):
                    print("Debug - No followed content")
                    return {
                        'events': [],
                        'followed_journeys': [],
                        'followed_users': [],
                        'followed_locations': [],
                        'pagination': {'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
                    }
                
                # Get followed content IDs efficiently
                if filter_type is None or filter_type == 'journey':
                    cursor.execute("SELECT journey_id FROM followed_journeys WHERE follower_id = %s", [user_id])
                    journey_ids = [row['journey_id'] for row in cursor.fetchall()]
                else:
                    journey_ids = []
                    
                if filter_type is None or filter_type == 'user':
                    cursor.execute("SELECT followed_id FROM followed_users WHERE follower_id = %s", [user_id])
                    user_ids = [row['followed_id'] for row in cursor.fetchall()]
                else:
                    user_ids = []
                    
                if filter_type is None or filter_type == 'location':
                    cursor.execute("SELECT location_id FROM followed_locations WHERE follower_id = %s", [user_id])
                    location_ids = [row['location_id'] for row in cursor.fetchall()]
                else:
                    location_ids = []
                
                # Build conditions
                conditions = []
                params = []
                
                if journey_ids and (filter_type is None or filter_type == 'journey'):
                    journey_placeholders = ', '.join(['%s'] * len(journey_ids))
                    conditions.append(f"e.journey_id IN ({journey_placeholders})")
                    params.extend(journey_ids)
                
                if user_ids and (filter_type is None or filter_type == 'user'):
                    user_placeholders = ', '.join(['%s'] * len(user_ids))
                    conditions.append(f"j.user_id IN ({user_placeholders})")
                    params.extend(user_ids)
                
                if location_ids and (filter_type is None or filter_type == 'location'):
                    location_placeholders = ', '.join(['%s'] * len(location_ids))
                    conditions.append(f"e.location_id IN ({location_placeholders})")
                    params.extend(location_ids)
                
                if not conditions:
                    return {
                        'events': [],
                        'followed_journeys': [],
                        'followed_users': [],
                        'followed_locations': [],
                        'pagination': {'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
                    }
                
                # Build main query with reason flags
                query = f"""
                SELECT 
                    e.event_id, e.title, e.description, e.start_date, e.end_date, 
                    e.create_time, e.update_time, e.user_id as event_user_id,
                    e.journey_id, j.title AS journey_title, 
                    e.location_id, l.name AS location_name,
                    j.user_id, u.username, u.first_name, u.last_name,
                    MAX(CASE WHEN e.journey_id IN ({', '.join(['%s'] * len(journey_ids) if journey_ids else ['0'])}) THEN 1 ELSE 0 END) AS is_followed_journey,
                    MAX(CASE WHEN j.user_id IN ({', '.join(['%s'] * len(user_ids) if user_ids else ['0'])}) THEN 1 ELSE 0 END) AS is_followed_user,
                    MAX(CASE WHEN e.location_id IN ({', '.join(['%s'] * len(location_ids) if location_ids else ['0'])}) THEN 1 ELSE 0 END) AS is_followed_location
                FROM events e
                JOIN journeys j ON e.journey_id = j.journey_id
                JOIN locations l ON e.location_id = l.location_id
                JOIN users u ON j.user_id = u.user_id
                WHERE ({' OR '.join(conditions)})
                AND (j.status = 'public' OR j.status = 'published')
                AND j.hidden = 0
                GROUP BY e.event_id
                ORDER BY e.update_time DESC
                LIMIT %s OFFSET %s
                """
                
                # Add all params for the reasons flags
                all_params = []
                if journey_ids:
                    all_params.extend(journey_ids)
                if user_ids:
                    all_params.extend(user_ids)
                if location_ids:
                    all_params.extend(location_ids)
                
                # Add the main query params
                all_params.extend(params)
                
                # Add pagination params
                all_params.extend([per_page, offset])
                
                print(f"Debug - Query: {query}")
                print(f"Debug - Params Count: {len(all_params)}")
                
                try:
                    # Execute the query
                    cursor.execute(query, all_params)
                    events = cursor.fetchall()
                    print(f"Debug - Found {len(events)} events")
                except Exception as e:
                    print(f"Debug - Error executing query: {str(e)}")
                    events = []
                
                # Get total count efficiently
                if events:
                    count_query = f"""
                    SELECT COUNT(DISTINCT e.event_id) as total
                    FROM events e
                    JOIN journeys j ON e.journey_id = j.journey_id
                    JOIN locations l ON e.location_id = l.location_id
                    JOIN users u ON j.user_id = u.user_id
                    WHERE ({' OR '.join(conditions)})
                    AND (j.status = 'public' OR j.status = 'published')
                    AND j.hidden = 0
                    """
                    count_params = params
                    cursor.execute(count_query, count_params)
                    total_count = cursor.fetchone()['total']
                else:
                    total_count = 0
                
                # Get followed content details
                cursor.execute("""
                SELECT fj.*, j.title 
                FROM followed_journeys fj
                JOIN journeys j ON fj.journey_id = j.journey_id
                WHERE fj.follower_id = %s
                """, [user_id])
                followed_journeys = cursor.fetchall()
                
                cursor.execute("""
                SELECT fu.*, u.username 
                FROM followed_users fu
                JOIN users u ON fu.followed_id = u.user_id
                WHERE fu.follower_id = %s
                """, [user_id])
                followed_users = cursor.fetchall()
                
                cursor.execute("""
                SELECT fl.*, l.name 
                FROM followed_locations fl
                JOIN locations l ON fl.location_id = l.location_id
                WHERE fl.follower_id = %s
                """, [user_id])
                followed_locations = cursor.fetchall()
                
                # Process events to add reasons and fetch images
                if events:
                    # Get all event IDs
                    event_ids = [event['event_id'] for event in events]
                    id_list = ', '.join(['%s'] * len(event_ids))
                    
                    # Fetch all images in one query
                    cursor.execute(f"""
                    SELECT event_id, image_id, image_path, upload_time
                    FROM event_images
                    WHERE event_id IN ({id_list})
                    ORDER BY event_id, upload_time
                    LIMIT 1000  # Safety limit to prevent too many images
                    """, event_ids)
                    
                    all_images = cursor.fetchall()
                    
                    # Group images by event
                    image_map = {}
                    for img in all_images:
                        if img['event_id'] not in image_map:
                            image_map[img['event_id']] = []
                        if len(image_map[img['event_id']]) < 10:  # Keep limit for UI performance
                            image_map[img['event_id']].append({
                                'image_id': img['image_id'],
                                'image_path': img['image_path'],
                                'upload_time': img['upload_time']
                            })
                    
                    # Add reasons and images to events
                    for event in events:
                        event['reasons'] = []
                        
                        # Add reasons based on flags
                        if event.get('is_followed_journey') == 1:
                            event['reasons'].append({
                                'type': 'journey',
                                'id': event['journey_id'],
                                'name': event['journey_title']
                            })
                        
                        if event.get('is_followed_user') == 1:
                            event['reasons'].append({
                                'type': 'user',
                                'id': event['user_id'],
                                'name': event['username']
                            })
                        
                        if event.get('is_followed_location') == 1:
                            event['reasons'].append({
                                'type': 'location',
                                'id': event['location_id'],
                                'name': event['location_name']
                            })
                        
                        # Add images from the map
                        event['images'] = image_map.get(event['event_id'], [])
                        
                        # Remove flag fields as they're not needed in the output
                        for field in ['is_followed_journey', 'is_followed_user', 'is_followed_location']:
                            if field in event:
                                del event[field]
            
            return {
                'events': events,
                'followed_journeys': followed_journeys,
                'followed_users': followed_users,
                'followed_locations': followed_locations,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total_count + per_page - 1) // per_page
                }
            }
        except Exception as e:
            print(f"Debug - Error: {str(e)}")
            flash(f"Error retrieving departure board events: {e}")
            return {
                'events': [],
                'followed_journeys': [],
                'followed_users': [],
                'followed_locations': [],
                'pagination': {
                    'total': 0,
                    'page': 1,
                    'per_page': per_page,
                    'pages': 0
                }
            }
        
    @staticmethod
    def unfollow_journey(user_id, journey_id):
        """Unfollow a journey"""
        try:
            query = """
            DELETE FROM followed_journeys 
            WHERE follower_id = %s AND journey_id = %s
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, [user_id, journey_id])
                return cursor.rowcount > 0
        except Exception as e:
            flash(f"Error unfollowing journey: {e}")
            return False
            
    @staticmethod
    def unfollow_user(user_id, followed_id):
        """Unfollow a user"""
        try:
            query = """
            DELETE FROM followed_users 
            WHERE follower_id = %s AND followed_id = %s
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, [user_id, followed_id])
                return cursor.rowcount > 0
        except Exception as e:
            flash(f"Error unfollowing user: {e}")
            return False
            
    @staticmethod
    def unfollow_location(user_id, location_id):
        """Unfollow a location"""
        try:
            query = """
            DELETE FROM followed_locations 
            WHERE follower_id = %s AND location_id = %s
            """
            
            with db.get_cursor() as cursor:
                cursor.execute(query, [user_id, location_id])
                return cursor.rowcount > 0
        except Exception as e:
            flash(f"Error unfollowing location: {e}")
            return False