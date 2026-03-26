from flask import Blueprint, flash, redirect, render_template, request,session, url_for
from app.premium.view import generate_expiring_notifications, revert_user_after_subscription_expired,update_subscription_expiry_date
from app.model import UserRepository
from datetime import datetime, timedelta

scheduler = Blueprint('scheduler', __name__)

@scheduler.route('/scheduletask', methods=['GET'])
def scheduletask():
    subscription_history = UserRepository.get_subscription_history(session['user_id'])
    return render_template('scheduler.html', subscription_history=subscription_history)

@scheduler.route('/runscheduler', methods=['POST'])
def runscheduler():
    
    if request.method == 'POST' and 'schedule_date' in request.form:
        schedule_date = request.form['schedule_date']
        
        # update the subscription expiry date
        schedule_datetime = datetime.strptime(schedule_date, '%Y-%m-%d')
        update_subscription_expiry_date(session['user_id'], schedule_datetime)
        
        generate_expiring_notifications()
        revert_user_after_subscription_expired()
        
        # update user session
        from app.auth.view import update_session
        update_session(session['user_id'])

    return redirect(request.referrer)        