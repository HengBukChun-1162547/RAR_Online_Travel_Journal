from flask import Blueprint, flash, render_template, request
from app.gamification.service import GamificationService
from app.auth.view import requires_permission

gamification = Blueprint('gamification', __name__)

gamification_service = GamificationService()

@gamification.route('/public-leaderboard/')
@requires_permission('view_leader_board')
def get_top_achievers_details():
    
    top_achievers = gamification_service.get_top_achievers()
    recent_achievements = gamification_service.get_recently_achieved_details()
    
    return render_template('public_leaderboard.html', top_achievers = top_achievers, 
                                                        recent_achievements = recent_achievements)
    
    
    
    