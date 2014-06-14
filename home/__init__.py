"""
home.__init__
=============

A simple module that defines how the flask app is created.

"""
__version__ = '0.3.4'

from os import environ

from flask import Flask
from flask.ext.admin import Admin
from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy

from home.ts.redis import RedisSeries


db = SQLAlchemy()
redis_series = RedisSeries()
login_manager = LoginManager()


def create_app(config=None):
    """ This needs some tidying up. To avoid circular imports we import
    everything here but it makes this method a bit more gross.
    """
    from home.api.api import api
    from home.api.models import User
    from home.api.admin import setup_admin

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'ssh, its a secret.'

    # Load the default config, the specified config file and then any
    # overwrites that are manually passed in.
    app.config.from_object('home.config')

    if 'HOME_SETTINGS' in environ:
        app.config.from_envvar('HOME_SETTINGS')

    app.config.from_object(config)

    app.register_blueprint(api, url_prefix='/api')

    login_manager.init_app(app)
    login_manager.login_view = 'Dashboard Web.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialise the migrations app, we want to store all migrations within
    # the project directory for easier packaging.
    Migrate(app, db, directory=app.config['MIGRATE_DIRECTORY'])

    admin = Admin(app)

    setup_admin(admin)

    # Wire up the database to the app so it gets the config.
    db.init_app(app)

    return app
