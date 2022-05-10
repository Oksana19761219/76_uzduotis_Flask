from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, IntegerField, EmailField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from flask_wtf.file import FileField, FileAllowed
from library_project import app


class RegistrationForm(FlaskForm):
    name = StringField('name', [DataRequired()])
    email = StringField('email', [DataRequired()])
    password = PasswordField('password', [DataRequired()])
    confirmed_password = PasswordField('repeat password', [EqualTo('password', 'incorrect password confirm')])
    submit = SubmitField('Register')

    def check_name(self, name):
        user = app.User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('This name has been used, choose another')

    def check_email(self, email):
        user = app.User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email has been used, choose another')


class LoginForm(FlaskForm):
    email = StringField('email', [DataRequired()])
    password = PasswordField('password', [DataRequired()])
    remember = BooleanField("remember me")
    submit = SubmitField('login')


class BibliographyForm(FlaskForm):
    author = StringField('author')
    title = StringField('title', [DataRequired()])
    year = IntegerField('year', [DataRequired()])
    submit = SubmitField('submit')


class AccountUpdateForm(FlaskForm):
    name = StringField('name', [DataRequired()])
    email = StringField('email', [DataRequired()])
    image = FileField('Update profile image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('update')

    def check_name(self, name):
        if name.data != app.current_user.name:
            user = app.User.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('This name has been used, choose another')

    def check_email(self, email):
        if email.data != app.current_user.email:
            user = app.User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email has been used, choose another')


class QueryUpdateForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordUpdateForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    confirmed_password = PasswordField('repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('change password')