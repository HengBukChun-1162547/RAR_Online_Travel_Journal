from flask import current_app, session, flash
from app.model import *
from datetime import datetime

class GamificationService:
    def __init__(self):
        self.gamification_repo = GamificationRepository()
    
    def get_achievement_types(self):
        """Get all achievement types"""
        return self.gamification_repo.get_achievement_types()
    
    def get_user_achievements_with_progress(self, user_id):
        """Get user's achievements and progress data"""
        return self.gamification_repo.get_user_achievements_with_progress(user_id)
    
    def get_user_achievement_progress_dict(self, user_id):
        """Get user's achievement progress as a dictionary keyed by achievement_type_id"""
        achievements_data = self.get_user_achievements_with_progress(user_id)
        result = {}
        
        for data in achievements_data:
            if data.get('achievement_progress_id') is not None:
                achievement_info = {
                    'current_value': data.get('current_value', 0) ,
                    'target_value': data.get('target_value', 0),
                    'unlocked_at': data.get('unlocked_at'),
                    'is_unlocked': data.get('unlocked_at') is not None
                }
                result[data['achievement_type_id']] = achievement_info
        
        return result
    
    def check_achievement(self, user_id, achievement_type_id, journey_id=None):
        """Check if the user has achieved a specific achievement type"""
        result = None
        message = None
        achievement_type = self.gamification_repo.get_achievement_types(achievement_type_id=achievement_type_id)
        if achievement_type_id not in session['achievements']:
            # Creating the First Journey
            if achievement_type_id == 1:
                target_value = current_app.config['ACHIEVEMENT_TYPE_1_TARGET_VALUE']
                journey_count = len(JourneyRepository.get_journeys(role=None, user_id=user_id, page_auth=None))
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                new_current_value = journey_count if journey_count else 0
                if journey_count and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif journey_count and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Creating the First Event
            elif achievement_type_id == 2:
                target_value = current_app.config['ACHIEVEMENT_TYPE_2_TARGET_VALUE']
                event_count = len(EventRepository.get_event_details(user_id=user_id))
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                new_current_value = event_count if event_count else 0
                if event_count and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif event_count and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Creating the Journey as Public
            elif achievement_type_id == 3:
                target_value = current_app.config['ACHIEVEMENT_TYPE_3_TARGET_VALUE']
                journeys = JourneyRepository.get_journeys(role=None, user_id=user_id, page_auth=None)
                public_journeys = [j for j in journeys if j['status'] == 'public']
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                new_current_value = len(public_journeys) if public_journeys else 0
                if public_journeys and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif public_journeys and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Visit More Than 20 Locations
            elif achievement_type_id == 4:
                target_value = current_app.config['ACHIEVEMENT_TYPE_4_TARGET_VALUE']
                event_locations = EventRepository.get_events(user_id=user_id)
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                new_current_value = len(event_locations) if event_locations else 0
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Longest Journey
            elif achievement_type_id == 5:
                target_value = current_app.config['ACHIEVEMENT_TYPE_5_TARGET_VALUE']
                journeys = JourneyRepository.get_journeys(role=None, user_id=user_id, page_auth=None)
                oldest_journey = min(journeys, key=lambda j: j['create_time'], default=None)
                days_old = None
                if oldest_journey:
                    days_old = datetime.now().date() - oldest_journey['create_time'].date()
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                new_current_value = days_old.days if days_old else None
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # View a Newly Shared Journey
            elif achievement_type_id == 6:
                target_value = current_app.config['ACHIEVEMENT_TYPE_6_TARGET_VALUE']
                journey_views = self.gamification_repo.get_journey_views_first_user(user_id=user_id)
                new_current_value = len(journey_views) if journey_views else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # First Report Submitted
            elif achievement_type_id == 7:
                target_value = current_app.config['ACHIEVEMENT_TYPE_7_TARGET_VALUE']
                report = self.gamification_repo.get_support_requests(user_id)
                new_current_value = len(report) if report else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if report and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif report and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Make Comment on the Bug/Help/Appeal Request
            elif achievement_type_id == 8:
                target_value = current_app.config['ACHIEVEMENT_TYPE_8_TARGET_VALUE']
                comment = self.gamification_repo.get_support_comments(user_id)
                new_current_value = len(comment) if comment else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if comment and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value) 
                elif comment and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Create at Least 5 Bug/Help/Appeal Request
            elif achievement_type_id == 9:
                target_value = current_app.config['ACHIEVEMENT_TYPE_9_TARGET_VALUE']
                report = self.gamification_repo.get_support_requests(user_id)
                new_current_value = len(report) if report else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if report and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value) 
                elif report and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # View the Complete Edit History of My Shared Journeys and Events
            elif achievement_type_id == 10:
                target_value = current_app.config['ACHIEVEMENT_TYPE_10_TARGET_VALUE']
                edit_logs = self.gamification_repo.get_edit_notifications(user_id)
                read_edit_logs = [log for log in edit_logs if log['is_read'] == 1]
                new_current_value = len(read_edit_logs) if edit_logs else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value) 
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Create First "No Edit" Journey
            elif achievement_type_id == 11:
                target_value = current_app.config['ACHIEVEMENT_TYPE_11_TARGET_VALUE']
                journeys = JourneyRepository.get_journeys(role=None, user_id=user_id, page_auth=None)
                no_edit_journeys = [j for j in journeys if j['no_edits'] == 1]
                new_current_value = len(no_edit_journeys) if no_edit_journeys else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Follow First "Shared Journey"
            elif achievement_type_id == 12:
                target_value = current_app.config['ACHIEVEMENT_TYPE_12_TARGET_VALUE']
                followed_journeys = self.gamification_repo.get_followed_journeys(user_id)
                new_current_value = len(followed_journeys) if followed_journeys else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Follow Any User Who is Shared His Journey Public
            elif achievement_type_id == 13:
                target_value = current_app.config['ACHIEVEMENT_TYPE_13_TARGET_VALUE']
                follwer_users = self.gamification_repo.get_followed_users(user_id)
                new_current_value = len(follwer_users) if follwer_users else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # First Journey a User Publishes on the Homepage
            elif achievement_type_id == 14:
                target_value = current_app.config['ACHIEVEMENT_TYPE_14_TARGET_VALUE']
                journeys = JourneyRepository.get_journeys(role=None, user_id=user_id, page_auth=None)
                published_journeys = [j for j in journeys if j['status'] == 'published']
                new_current_value = len(published_journeys) if published_journeys else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)
            # Earn an Achievement When Adding a Cover Image to Five Journeys
            elif achievement_type_id == 15:
                target_value = current_app.config['ACHIEVEMENT_TYPE_15_TARGET_VALUE']
                journeys = JourneyRepository.get_journeys(role=None, user_id=user_id, page_auth=None)
                journeys_with_cover = [j for j in journeys if j['cover_image'] is not None and j['cover_image'] != '']
                new_current_value = len(journeys_with_cover) if journeys_with_cover else 0
                user_achievement_progress = self.gamification_repo.get_user_achievement_progress(user_id, achievement_type_id)
                if new_current_value and user_achievement_progress is None:
                    result = GamificationRepository.create_user_achievement_progress(user_id, achievement_type_id, new_current_value, target_value)
                elif new_current_value and user_achievement_progress is not None and user_achievement_progress['current_value'] < user_achievement_progress['target_value']:
                    new_current_value = new_current_value if new_current_value >= user_achievement_progress['current_value'] else user_achievement_progress['current_value']
                    result = GamificationRepository.update_user_achievement_progress(user_id, achievement_type_id, new_current_value)        
            else:
                # Placeholder for additional achievement types
                result = None
            
            # If the achievement reached the target value, create the user achievement
            if result:
                if target_value <= new_current_value:
                    result = GamificationRepository.create_user_achievement(user_id, achievement_type_id)
                    from app.auth.view import update_session
                    update_session(user_id)
                    if result:
                        message = f"Congratulations! You have earned the achievement: {achievement_type_id} - {achievement_type['title']}"
                        result = NotificationRepository.create_system_notification(user_id, message, 'Achievement')
                        flash(message, 'success')
        else:
            # If the achievement type is already in session, it means the user has already achieved it.
            result = None
        return result
    
    def get_top_achievers(self):
        return self.gamification_repo.get_top_achievers_details(current_app.config['ACHIEVEMENT_LEADERBOARD_TOP_LIMIT'])
    
    
    def get_recently_achieved_details(self):
        return self.gamification_repo.get_recently_achieved_details(current_app.config['ACHIEVEMENT_LEADERBOARD_RECENT_LIMIT'])
        
    
    
    