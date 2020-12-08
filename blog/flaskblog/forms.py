from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
     validators=[DataRequired(), Length(min=2,max=20)])

    email = StringField('Email',
     validators=[DataRequired(), Email()])

    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
     validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken!! Choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email ID taken!! Choose a different one.')


class LoginForm(FlaskForm):

    email = StringField('Email',
     validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()],id='pass') 
    show_pass = BooleanField('Show Password',id='show')
    
    submit = SubmitField('Login') #These are values for buttons



class EditProfileForm(FlaskForm):
    username = StringField('Username',
     validators=[ Length(min=2,max=20)])

    email = StringField('Email',
     validators=[Email()])

    bio = StringField('Bio',
    validators=[Length(max=100)])

    pic = FileField('Edit',validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Save Changes')

    def validate_username(self, username):
        #if edited username is not equal to current username then and then only validation will be performed.
        if username.data != current_user.username: 
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username taken!! Choose a different one.')

    def validate_email(self, email):
        #if edited email is not equal to current email then and then only validation will be performed.
        if email.data != current_user.email:     
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email ID taken!! Choose a different one.')



class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()])
    category = StringField('Category',validators=[DataRequired()])
    submit = SubmitField('Post')


class SearchForm(FlaskForm):
    category = StringField('Search Category',validators=[DataRequired()])
    search = SubmitField('Search')

class CommentForm(FlaskForm):
    content = StringField('Comment',validators=[DataRequired()])
    submit = SubmitField('Post Comment')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
