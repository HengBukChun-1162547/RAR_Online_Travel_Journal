from flask import flash
from app import db

class JourneyRepository:
    @staticmethod
    def add_journey(user_id, title, description, start_date, status):
        """add the journey to the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''INSERT INTO journeys (user_id, title, description, start_date, status) VALUES (%s, %s, %s, %s, %s);'''
                            , (user_id, title, description, start_date, status))
                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to add journey! ' + e, 'error')
            return False

    @staticmethod
    def update_journey(user_id, title, description, start_date, status, journey_id, cover_image='__UNCHANGED__'):
        """update the journey in the database"""
        try:
            param = []
            str_sql = '''UPDATE journeys SET title = %s,
                                        description = %s,
                                        start_date = %s,
                                        update_by = %s
                        '''
            param = [title, description, start_date, user_id]
            if status:
                str_sql += ''', status = %s '''
                param.append(status)
            # Only update cover_image if explicitly provided (not the default value)
            if cover_image != '__UNCHANGED__':
                str_sql += ''', cover_image = %s '''
                param.append(cover_image)
            str_sql += ''' WHERE journey_id = %s;'''
            param.append(journey_id)

            with db.get_cursor() as cursor:
                cursor.execute(str_sql, param)
                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to update journey! ' + str(e), 'error')
            return False

    @staticmethod
    def hide_journey(journey_id, is_hide):
        """hide or unhide the journey in the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''UPDATE journeys SET hidden = %s,
                                    update_time = (SELECT update_time FROM (SELECT update_time FROM journeys WHERE journey_id = %s) AS temp)
                                    WHERE journey_id = %s;
                            '''
                            , (is_hide, journey_id, journey_id))

                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to hide/unhide journey! ' + e, 'error')
            return False

    @staticmethod
    def toggle_no_edits(journey_id, no_edits_value):
        """Set the no_edits flag for a journey"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''UPDATE journeys SET no_edits = %s,
                                    update_time = (SELECT update_time FROM (SELECT update_time FROM journeys WHERE journey_id = %s) AS temp)
                                    WHERE journey_id = %s;
                            '''
                            , (no_edits_value, journey_id, journey_id))

                result = cursor.rowcount
                if result > 0:
                    return True
                else:
                    return False
        except Exception as e:
            flash('Failed to update no_edits flag! ' + str(e), 'error')
            return False

    @staticmethod
    def delete_journey(journey_id):
        """delete the journey from the database"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute('''DELETE FROM journeys WHERE journey_id = %s;'''
                        , (journey_id,))
                result = cursor.rowcount
                if result > 0:
                    return True
                return False
        except Exception as e:
            flash('Failed to delete journey! ' + e, 'error')
            return False


    @staticmethod
    def get_journeys(role, user_id, page_auth, journey_id=None, show_hidden=None, view_hidden_journey=None, searchby=None, search_input=None):
        """get the journey from the database"""
        journeys = []
        str_sql = '''SELECT j.*, u.user_id as journey_user, u.status as user_status, u.username, r.role_name, u.profile_image, u2.username as updated_by, j.cover_image
                        FROM journeys j
                        LEFT JOIN users u ON j.user_id = u.user_id
                        LEFT JOIN users u2 ON j.update_by = u2.user_id
                        LEFT JOIN roles r ON u.role_id = r.role_id
                        WHERE 1=1
                    '''
        params = []
        # By Journey ID
        if journey_id:
            str_sql += ''' AND j.journey_id = %s'''
            params.append(journey_id)
        # Public Journeys
        elif page_auth == 'public':
            str_sql += ''' AND j.status IN (%s, %s)'''
            params.extend(['public', 'published'])
            if searchby == '1':
                str_sql += ''' AND j.title LIKE %s'''
                params.append(f'%{search_input[0]}%')
            if searchby == '2':
                str_sql += ''' AND j.description LIKE %s'''
                params.append(f'%{search_input[0]}%')
            if searchby == '3':
                str_sql += ''' AND (j.title LIKE %s OR j.description LIKE %s) '''
                params.append(f'%{search_input[0]}%')
                params.append(f'%{search_input[0]}%')
            if searchby == '4':
                str_sql += ''' AND j.journey_id in('''
                if search_input:
                    for value in search_input:
                        str_sql += '''%s,'''
                        params.append(f'{value}')
                else:
                    str_sql += '''%s,'''
                    params.append("''")
                str_sql = str_sql[:-1] + ''') '''
            if searchby == '5':
                str_sql += ''' AND u.username LIKE %s'''
                params.append(f'%{search_input[0]}%')
                
            if not view_hidden_journey:
                str_sql += ''' AND j.hidden = %s'''
                params.append(0)
                str_sql += ''' ORDER BY j.update_time DESC'''
            else:
                # only show hidden journeys and order by user
                if show_hidden == '1':
                    str_sql += ''' AND j.hidden = %s'''
                    params.append(show_hidden)
                    str_sql += ''' ORDER BY j.user_id'''
                # show all journeys and order by update time
                else:
                    str_sql += ''' ORDER BY j.update_time DESC'''

        elif page_auth == 'published':
            str_sql += ''' AND j.hidden = %s'''
            params.append(show_hidden)
            str_sql += ''' AND j.status = %s'''
            params.append(page_auth)
            str_sql += ''' AND r.role_name != %s'''
            params.append('traveller')
            str_sql += ''' ORDER BY j.update_time DESC'''


        # My Journeys
        else:
            str_sql += ''' AND j.user_id = %s
                            ORDER BY j.start_date DESC, j.create_time DESC
                        '''
            params.append(user_id)

        try:
            with db.get_cursor() as cursor:
                cursor.execute(str_sql, params)
                if journey_id:
                    journeys = cursor.fetchone()
                else:
                    journeys = cursor.fetchall()
        except Exception as e:
            flash('Failed to get journeys! ' + e, 'error')
        return journeys

    @staticmethod
    def get_journey(journey_id):
        try:
            with db.get_cursor() as cursor:
                str_sql = '''SELECT * FROM journeys WHERE journey_id = %s'''
                params = [journey_id]
                cursor.execute(str_sql, params)
                return cursor.fetchone()
        except Exception as e:
            flash(f"Error retrieving journey data: {e}")
            return None

    @staticmethod
    def get_journey_count(user_id=None, status=None):
        """get the count of journeys from the database"""
        try:
            with db.get_cursor() as cursor:
                str_sql = '''SELECT COUNT(*) as count FROM journeys WHERE 1=1'''
                params = []
                if user_id:
                    str_sql += ''' AND user_id = %s'''
                    params.append(user_id)
                if status:
                    str_sql += ''' AND status = %s'''
                    params.append(status)
                    str_sql += ''' AND hidden = %s'''
                    params.append(0)
                cursor.execute(str_sql, params)
                return cursor.fetchone()
        except Exception as e:
            flash('Failed to get journey count! ' + e, 'error')
            return None