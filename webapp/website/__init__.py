from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "baby"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mySuperSecretKey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://babyapp:Babyapp123!@mysql_server/{DB_NAME}'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Child, History

    
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    return app

def create_database(app):
    # if not path.exists('./DB/' + DB_NAME):
    with app.app_context():
        db.create_all()
    print('Created DATABASE!')


