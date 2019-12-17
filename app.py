from flask import Flask

# import flask login
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# create secret key
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQL']

# create login manager and pass app
login_manager = LoginManager(app)
db = SQLAlchemy(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
