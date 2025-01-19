# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from importlib import import_module


db = SQLAlchemy()
ckeditor = CKEditor()
login_manager = LoginManager()
migrate = Migrate()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home', 'api', 'blog'):
        module = import_module('apps.{}.routes'.format(module_name))
        # Try standard blueprint name first, then module-specific name
        blueprint = getattr(module, 'blueprint', None) or \
                   getattr(module, f'{module_name}_bp', None)
        if blueprint:
            app.register_blueprint(blueprint)
        else:
            print(f'> Warning: No blueprint found for module {module_name}')


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

from apps.authentication.oauth import github_blueprint

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    app.register_blueprint(github_blueprint, url_prefix="/login")    
    configure_database(app)
    return app
