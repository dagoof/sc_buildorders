import functools, operator, datetime
import flask, bcrypt
import func_utils, decorators, sc_units, sc_orders
from build_orders import app, models, forms, flask_decorators, permissions

api_func = decorators.apply_f(decorators.obj_to_kwargs(flask.jsonify))

@app.route('/')
def index():
    return flask.redirect(flask.url_for('builds'))

def _unit_options(unit):
    return func_utils.map_sub(str, sc_units.all_gameunits[unit].data_obj)

@app.route('/api/unit_options/<unit>')
@api_func
def api_unit_options(*args, **kwargs):
    return _unit_options(*args, **kwargs)

@app.route('/unit_options/<unit>')
def unit_options(*args, **kwargs):
    return flask.render_template('create.html',
            **_unit_options(*args, **kwargs))

@app.route('/user/register', methods = ['GET', 'POST'])
def user_register():
    form = forms.RegistrationForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        user = models.User(**forms.form_values(form))
        if models.can_commit(user):
            return flask.redirect(flask.url_for('index'))
        else:
            flask.flash('Profile already exists')
    return flask.render_template('generic_form.html', form = form)

@app.route('/user/login', methods = ['GET', 'POST'])
def user_login():
    form = forms.LoginForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        user = models.User.query.filter_by(email = form.email.data).first()
        if user and user.check_password(form.password.data):
            flask.session[models.User.SESSION_KEY] = user.username
            return flask.redirect(flask.url_for('index'))
        else:
            if user:
                flask.flash('Invalid password')
            else:
                flask.flash('User not found')
    return flask.render_template('generic_form.html', form = form)

@app.route('/user/logout')
@flask_decorators.login_required
def user_logout():
    flask.session.pop(models.User.SESSION_KEY, None)
    return flask.redirect(flask.url_for('index'))

@app.route('/user/builds')
@flask_decorators.login_required
def user_builds():
    builds = models.BuildDetails.query.filter_by(user = flask.g.user)
    return flask.render_template('builds.html',
            builds = map(operator.attrgetter('build'), builds))

@app.route('/build/create')
@flask_decorators.login_required
def build_create():
    return flask.render_template('create.html', races = sc_units.Races.races)

@app.route('/build/<int:build_id>')
def build(build_id):
    build = models.Build.query.filter_by(id = build_id).first()
    return flask.render_template('build.html', build = build)

@app.route('/builds')
def builds():
    builds = models.Build.query.all()
    return flask.render_template('builds.html', builds = builds)

@app.route('/build/create/<race>')
@flask_decorators.login_required
def build_create_race(race):
    build = models.Build.from_order(race, sc_orders.race_builds[race])
    return flask.redirect(flask.url_for('build', build_id = build.id))

@app.route('/build/add/<int:build_id>/<unit>')
@flask_decorators.login_required
def build_add(build_id, unit):
    build = models.Build.query.filter_by(id = build_id).first()
    build.add_unit(unit)
    return flask.redirect(flask.url_for('build', build_id = build_id))

@app.route('/event/player_list')
@api_func
def event_player_list():
    return { 'players': map(str, models.Player.query.all()) }

@app.route('/event/<int:event_id>')
def event(event_id):
    event = models.Event.query.filter_by(id = event_id).first()
    return flask.render_template('event.html', event = event)

#@flask_decorators.permission_required(permissions.Permissions.CREATE_EVENT)
@app.route('/event/create', methods = ['GET', 'POST'])
@flask_decorators.login_required
def event_create():
    form = forms.EventForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        event = models.Event(**forms.form_values(form))
        if models.can_commit(event):
            return flask.redirect(flask.url_for('event', event_id = event.id))
        flask.flash('Event name already exists')
    return flask.render_template('event_form.html', form = form)
