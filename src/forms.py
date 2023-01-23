from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[validators.Email(), validators.DataRequired()])
    name = StringField('Name', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])


class ChatForm(FlaskForm):
    message = StringField('Message')

class ReplyForm(FlaskForm):
    message = StringField('Message', validators=[validators.DataRequired()])
