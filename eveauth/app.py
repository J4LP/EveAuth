import os
from flask import Flask, session
import yaml
from flask_wtf import CsrfProtect

csrf = CsrfProtect()


def create_app(config_file=None, config_object=None):
    """
    Application bootstrapper.
    """
    app = Flask(__name__, static_folder='public')
    app.config.from_object('eveauth.settings.BaseConfig')
    app.environment = os.getenv('eveauth_ENV', 'dev')

    if config_file:
        file_ext = os.path.splitext(config_file)[1]
        if file_ext == '.yml':
            with open(config_file) as f:
                config_yaml = yaml.load(f)
                app.config.update(**config_yaml)
        elif file_ext == '.py':
            app.config.from_pyfile(config_file)
        else:
            raise Exception('Unsupported config file format: {}, expecting Yaml or Python'.format(file_ext))

    if config_object:
        app.config.update(**config_object)

    if app.environment != 'test':
        csrf.init_app(app)

    from eveauth.api import api_manager
    api_manager.init_app(app)

    from eveauth.models import db, migrate, ma
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    from eveauth.controllers import MetaView
    MetaView.register(app)

    from eveauth.services import sso_service
    sso_service.init_app(app)

    app.add_template_global(app.config, 'config')

    return app
