from flask import Flask, session, redirect, url_for, request, flash
from flask_bcrypt import Bcrypt
from datetime import timedelta
from app import connect
from app import db
from app.config import Config

from app.utils import Utils, Pagination, register_template_utils

# Create the Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)
app.secret_key = 'Online_Travel_Journal'
# Set the session lifetime for security reasons
app.permanent_session_lifetime = timedelta(minutes=30)

"""Create an instance of the Bcrypt class, which we'll be using to hash user
    passwords during login and registration.
"""
flask_bcrypt = Bcrypt(app)

# Initialize the database
db.init_db(app, connect.dbuser, connect.dbpass, connect.dbhost, connect.dbname)

"""! Register blueprints."""
from .auth.view import auth as auth_blueprint
from .user import user as user_blueprint
from .journey.view import journey as journey_blueprint
from .event.view import event as event_blueprint
from .premium.view import premium as premium_blueprint
from .dpboard.view import departure_board as departure_board_blueprint
from .helpdesk.view import helpdesk
from .scheduler.view import scheduler
from .gamification.view import gamification
app.register_blueprint(auth_blueprint, url_prefix='')
app.register_blueprint(user_blueprint)
app.register_blueprint(journey_blueprint)
app.register_blueprint(event_blueprint)
app.register_blueprint(premium_blueprint)
app.register_blueprint(departure_board_blueprint)
app.register_blueprint(helpdesk)
app.register_blueprint(scheduler)
app.register_blueprint(gamification)

"""! Register utility functions."""
# Register template utility functions
register_template_utils(app)

# Import and register the CLI commands
from .commands import scheduler
app.cli.add_command(scheduler)