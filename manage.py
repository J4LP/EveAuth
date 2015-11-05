from flask.ext.script import Manager
from eveauth.app import create_app
from flask.ext.migrate import MigrateCommand

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config_file', required=False)
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
