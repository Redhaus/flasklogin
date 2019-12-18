from urllib.parse import urlparse, urljoin

from flask import Flask, render_template, request, session, redirect

# import flask login
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)

# create secret key
app.config['SECRET_KEY'] = 'mysecretkey'

# connect sql alchemy to db via uri
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://azzddqtspsqohw:79849f49882a552fe3316ba9d34862e2bd9af630c854aa1f642915a806bda7ae@ec2-174-129-32-230.compute-1.amazonaws.com:5432/d63gnu3irvef2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['USE_SESSION_FOR_NEXT'] = True

# create login manager and pass app
login_manager = LoginManager(app)

# create this default login view and it will redirect you to the login page
login_manager.login_view = 'login'

# set custom login message
login_manager.login_message = 'You need to login first'

serializer = URLSafeTimedSerializer(app.secret_key)

# create db connection with sqlalchemy
db = SQLAlchemy(app)

# URL parsing for safe urls
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target ))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# create a user model and also inherit from userMixin from Flask login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    session_token = db.Column(db.String(100), unique=True)

    # usermixen provides get id method to map user to db
    # when using alternative tokens you have to do it yourself
    def get_id(self):
        return self.session_token




# create connection between model and flask login
# using this decorator function
# load a user
# this is the gateway function that loads user if everything checks out
@login_manager.user_loader
def load_user(session_token):
    # serializer is opposite of dumps it takes in a token
    serializer.loads(session_token, )
    # search user by session_token
    return User.query.filter_by(session_token=session_token).first()


def create_user():
    user = User(username='benjamin', password='pass', session_token=serializer.dumps(['benjamin', 'pass']))
    db.session.add(user)
    db.session.commit()

def update_token():
    # return user obj
    benjamin = User.query.filter_by(username='benjamin').first()
    # update pw
    benjamin.password = 'password2'
    # generate a new token
    benjamin.session_token = serializer.dumps(['benjamin', 'password2'])
    db.session.commit()

# create a route to handle thing
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if post request get username from form
    # query db for user by username
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        # if user doesn't exist tell them'
        if not user:
            return 'user does not exist'

        # if user does exist then login and tell them
        login_user(user,remember=True)

        # this will check if there is a redirect var in the url
        if 'next' in session:
            next = session['next']

            print(next)

            # checking safe url function created above
            # if so and not none then redirect to it after login
            if is_safe_url(next) and next is not None:
                return redirect(next)

        return 'you are logged in'

    # this gets the previous page you were redirected from
    # so you can redirect back to it
    session['next'] = request.args.get('next')
    return render_template('login.html')


@app.route('/home')
@login_required
def home():
    return f'you are in protected area {current_user.username}'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'you are logged out'


@app.route('/')
def index():
    user = User.query.filter_by(username='benjamin').first()
    login_user(user, remember=True)
    return 'you are logged in!'


if __name__ == '__main__':
    app.run()