import flask
from build_orders import app, models

def logged_in():
    return getattr(flask.g, 'user', None)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not logged_in():
            return redirect(flask.url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    if models.User.SESSION_KEY in flask.session:
        flask.g.user = models.User.query.filter_by(\
                username = flask.session[models.User.SESSION_KEY]).first()

@app.after_request
def after_request(response):
    return response


