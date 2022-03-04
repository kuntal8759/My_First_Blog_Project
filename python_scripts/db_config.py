"""To Understand The Relationship Between The Databases, See "db_relationship_flowchart_1.png" and
"db_relationship_flowchart_2.png" Images Inside The Project Root Folder."""

# Import Required Modules & Scripts To Configure The Database.
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from python_scripts.app_config import app

# Creating Primary Database..
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../db//posts.db"

# Creating 2 Secondary Database & Bind Them With The Primary Database.
app.config["SQLALCHEMY_BINDS"] = {"user_data": "sqlite:///../db/user.db",
                                  "user_comments": "sqlite:///../db/comment.db"}
# Set Some Parameters of SQLAlchemy & Link It With Flask.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Configure The Database Table.
class User(UserMixin, db.Model):
    """This class deals with the creation of a table inside the database with predefined set of rules."""

    # Name Of The Table.
    __tablename__ = "user_details"

    # Set A "bind_key" To Link Multiple Databases Together.
    __bind_key__ = "user_data"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    uuid = db.Column(db.String(250), nullable=False)

    '''Create Relation To The BlogPost Object. The "author" Refers To The author Property Inside The BlogPost 
    Class. Act Like A List.'''
    post = db.relationship("BlogPost", back_populates="author")

    '''Create Relation To The Comment Object. The "comment_author" Refers To The comment_author Property 
    Inside The Comment Class. Act Like A List.'''
    comments = db.relationship("Comment", back_populates="comment_author")


# Configure The Database Table.
class BlogPost(UserMixin, db.Model):
    """This class deals with the creation of a table inside the database with predefined set of rules."""

    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Creating Foreign Key "users_details.id", This Refers To The "tablename" Of The User Class.
    author_id = db.Column(db.Integer, db.ForeignKey("user_details.id"), nullable=False)

    '''Create Relation To The User Object. The "post" Refers To The post Property Inside The User Class. 
    Act Like A List.'''
    author = db.relationship("User", back_populates="post")

    '''Create Relation To The Comment Object. The "parent_post" Refers To The parent_post Property Inside 
    The Comment Class. Act Like A List.'''
    comments = db.relationship("Comment", back_populates="parent_post")


class Comment(UserMixin, db.Model):
    """This class deals with the creation of a table inside the database with predefined set of rules."""

    __tablename__ = "comments"
    __bind_key__ = "user_comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)

    # Creating Foreign Key "users_details.id", This Refers To The "tablename" Of The User Class.
    author_id = db.Column(db.Integer, db.ForeignKey("user_details.id"), nullable=False)

    # Creating Foreign Key "blog_post.id", This Refers To The "tablename" Of The BlogPost Class.
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"), nullable=False)

    '''Create Relation To The User Object. The "comments" Refers To The comments Property Inside The User 
    Class. Act Like A List.'''
    comment_author = db.relationship("User", back_populates="comments")

    '''Create Relation To The BlogPost Object. The "comments" Refers To The comments Property Inside The 
    BlogPost Class. Act Like A List.'''
    parent_post = db.relationship("BlogPost", back_populates="comments")


# Creating Default & Other Databases.
db.create_all()
db.create_all(bind="user_data")
db.create_all(bind="user_comments")
