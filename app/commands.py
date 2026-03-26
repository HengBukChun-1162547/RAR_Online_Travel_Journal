import click
from flask.cli import with_appcontext

from app import db
from app.model.notification_repository import NotificationRepository
from app.model.subscription_repository import SubscriptionRepository
from app.model.user_repository import UserRepository
from app.premium.view import generate_expiring_notifications, revert_user_after_subscription_expired

@click.command(name='scheduler')
@with_appcontext
def scheduler():
    try:
        
        generate_expiring_notifications()
        revert_user_after_subscription_expired()
                
    except Exception as e:
        print('Failed to perform scheduled task! ' + str(e), 'error')
        return False
    
    