from flask import Blueprint

user = Blueprint('user', __name__)

from . import view
from . import admin
from . import subscription_controller
from . import notifications