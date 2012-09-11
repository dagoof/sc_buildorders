import wtforms

def form_values(form):
    return dict((f.short_name, f.data) for f in\
            form._fields.values())

class RegistrationForm(wtforms.Form):
    username = wtforms.TextField('Username',
            [wtforms.validators.Required()],
            description = 'Username of this profile')
    email = wtforms.TextField('Email',
            [wtforms.validators.Email(),
                wtforms.validators.Required()],
            description = 'A valid email address')
    password = wtforms.PasswordField('Password', 
            [wtforms.validators.Required(),
                wtforms.validators.EqualTo('password_confirm',
                    message = 'Passwords must match')],
                description = 'Password bound to profile')
    password_confirm = wtforms.PasswordField('Repeat Password',
            description = 'Repeat password to verify')

    def __str__(self):
        return 'Register'


class LoginForm(wtforms.Form):
    email = wtforms.TextField('Email',
            [wtforms.validators.required()],
            description = 'Enter your email')
    password = wtforms.PasswordField('Password',
            [wtforms.validators.required()],
            description = 'Your password')

    def __str__(self):
        return 'Login'

class EventForm(wtforms.Form):
    name = wtforms.TextField('Name',
            [ wtforms.validators.required() ],
            description = 'Unique name of this event')
    time = wtforms.DateField('Time',
            [ wtforms.validators.required() ],
            format = '%m/%d/%Y',
            description = 'Time that the event will occur')
    players = wtforms.FieldList(wtforms.TextField('Player'),
            min_entries = 2)


