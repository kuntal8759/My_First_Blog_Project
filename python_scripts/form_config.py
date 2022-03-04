# Import Required Modules & Scripts To Configure The Form Field.
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditor, CKEditorField
from python_scripts.app_config import app
from flask_wtf import FlaskForm
from dotenv import load_dotenv
import os

# Create CSRF Token Key.
load_dotenv("C:/Users/Kuntal Bhattacharjee/Desktop/Codes/Python Codes/70. Uploading Blog To Internet/.env")
app.config["SECRET_KEY"] = os.getenv("KEY")

# Connect CKEditor To The Flask Server.
ckeditor = CKEditor(app)


class CreatePostForm(FlaskForm):
    """This class create a form object that is used in the creation of a new post, in which the "body" field
    is of "CkeditorField" type."""

    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    """This class create a form object that is used in the registration of a new user."""

    name = StringField("Name", validators=[DataRequired(message="Can Not Be Empty"),
                                           Length(max=40, message="Enter A Valid Name")])
    email = EmailField("Email", validators=[DataRequired(), Email(message="Not A Valid Email Address",
                                                                  check_deliverability=True),
                                            Length(min=10, max=50, message="Not A Valid Email Address")])
    password = PasswordField("Password",
                             validators=[DataRequired(message="Enter Password"),
                                         Length(min=10, max=128,
                                                message="Password Must Be Within 10 To 128 Character Long")])
    submit = SubmitField("Submit", validators=[DataRequired()])


class LoginForm(FlaskForm):
    """This class create a form object that is used in the login of an existing user."""

    email = EmailField("Email", validators=[DataRequired(), Email(message="Not A Valid Email Address",
                                                                  check_deliverability=True),
                                            Length(min=10, max=50, message="Not A Valid Email Address")])
    password = PasswordField("Password",
                             validators=[DataRequired(message="Enter Password"),
                                         Length(min=10, max=128,
                                                message="Password Must Be Within 10 To 128 Character Long")])
    submit = SubmitField("Submit", validators=[DataRequired()])


class CommentForm(FlaskForm):
    """This class create a form object that is used in the commenting by a user. It input field is of
    "CkeditorField" type."""

    comments = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit", validators=[DataRequired()])
