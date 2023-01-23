from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, emit

db = SQLAlchemy()

socketio = SocketIO()


def format_datetime(datetime_obj):
    time_diff = datetime.now() - datetime_obj
    if time_diff.days > 0:
        return f"{time_diff.days} дней назад"
    elif time_diff.seconds > 3600:
        return f"{time_diff.seconds // 3600} часов назад"
    elif time_diff.seconds > 60:
        return f"{time_diff.seconds // 60} минут назад"
    else:
        return f"{time_diff.seconds} секунд назад"

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '333a046d6f43a1e61f1a1e7d83bb664af96776929a79b4847dee206d26b1cdc7'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:103891@127.0.0.1:5432/flask_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    socketio.init_app(app)



    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from src.models import User

    # with app.app_context():
    #     db.drop_all()

    # with app.app_context():
    #     db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # from .models import User
    #
    # with app.app_context():
    #     db.create_all()

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from src.models import Visit

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_visit = datetime.now()
            db.session.commit()
            visit = Visit(
                user_id=current_user.id,
                ip_address=request.remote_addr,
                browser=request.user_agent.browser
            )
            db.session.add(visit)
            db.session.commit()



        app.jinja_env.filters['format_datetime'] = format_datetime

    return app



# @app.route("/")
# def hello_world():
#     return "hi"
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#
#     def __init__(self, username, email, password):
#         self.username = username
#         self.email = email
#         self.password = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password, password)
#
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     new_user = User(username=data['username'], email=data['email'], password=data['password'])
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({'message': 'User created successfully'})
#
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = User.query.filter_by(email=data['email']).first()
#     if user and user.check_password(data['password']):
#         return jsonify({'message': 'Logged in successfully'})
#     else:
#         return jsonify({'message': 'Invalid email or password'})

# if __name__ == '__main__':
#     app.run()
