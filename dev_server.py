# Import Required Modules.
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, LoginManager, current_user, logout_user
from flask_gravatar import Gravatar
from functools import wraps
import datetime

# Import Custom Codes Required To Run The "dev_server" File.
from python_scripts.data_security_config import PasswordSecurity, DataSecurity, UserInputSecurity
from python_scripts.form_config import CreatePostForm, RegisterForm, LoginForm, CommentForm
from python_scripts.db_config import db, BlogPost, User, Comment
from python_scripts.app_config import app


# Creating Objects From Classes.
pw_security = PasswordSecurity()
data_security = DataSecurity()
user_input_security = UserInputSecurity()

# Creating "login_manager" Object & Link It With Flask "app" Instance.
login_manager = LoginManager()
login_manager.init_app(app)

# Link Flask "app" With Flask-Gravatar & Set Its Parameters.
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False,
                    use_ssl=False, base_url=None)


# Creating "user_loader" Callback To Reload The User Object From The User ID Stored In The Session.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Creating A Python Decorator To Identify The Admin.
def admin_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)

    return decorated_function


# Show All Post In Index Page.
@app.route('/')
def get_all_posts():
    # Calculate "current_year" And Pass That To Every HTML File, So That The "footer.html" Can Use It.
    current_year = datetime.datetime.now().year
    '''This line above is placed inside every route (in local scope instead of global scope), so that it 
    don't rely on an old value (if it was placed in global scope, the value was only be generated once when 
    the server started for the first time), and calculate "current_year" every time a page reloads.'''
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, year=current_year,
                           logged_in=current_user.is_authenticated)


# Creating Route To Register New User.
@app.route('/register', methods=["GET", "POST"])
def register():
    current_year = datetime.datetime.now().year
    register_form = RegisterForm()
    if register_form.validate_on_submit():

        # Check If User Already Exist In The Database.
        if User.query.filter_by(email=data_security.data_hash(request.form.get("email"))).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))
        else:
            # Creating The New User In The Database After Securing Their Data.
            new_user = User(
                name=request.form["name"],
                email=data_security.data_hash(request.form["email"]),
                password=pw_security.encrypt_password(request.form["password"])[1],
                uuid=pw_security.salt
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            # Pass In Name Of The Current User & Passing In The Current Login Status Of That User.
            return redirect(url_for("get_all_posts", logged_in=current_user.is_authenticated))
    return render_template("register.html", register_form=register_form,
                           logged_in=current_user.is_authenticated, year=current_year)


# Creating Route For The Existing User To Login.
@app.route('/login', methods=["GET", "POST"])
def login():
    current_year = datetime.datetime.now().year
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")

        # Find User By Email Entered.
        user = User.query.filter_by(email=data_security.data_hash(email)).first()

        # If User Doesn't Exist.
        if not user:
            flash("Email Address Doesn't Exist")
            return redirect(url_for("login"))

        # If User Exist But Entered Password Is incorrect.
        elif not pw_security.decrypt_password(uuid=user.uuid, pwhash=user.password, password=password):
            flash("Password incorrect, please try again.")
            return redirect(url_for("login"))

        # If User Exists & Entered Password Is Correct.
        else:
            login_user(user)
            return redirect(url_for("get_all_posts"))
    return render_template("login.html", login_form=login_form, year=current_year)


# Creating Route For The Logged-In User To Log Out.
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


# Show Detailed Single Post When Clicked.
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    current_year = datetime.datetime.now().year
    requested_post = BlogPost.query.get(post_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                text=user_input_security.script_filter(comment_form.comments.data),
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
            # return render_template("post.html", post=requested_post, year=current_year,
            #                        current_user=current_user, logged_in=current_user.is_authenticated,
            #                        comment_form=comment_form, comments=comment_form.comments)
        else:
            # Show Error Message.
            flash("You Have To Login To Make A comment.")
            return redirect(url_for("login"))
    return render_template("post.html", post=requested_post, year=current_year, comment_form=comment_form,
                           current_user=current_user, logged_in=current_user.is_authenticated)


# Edit An Existing Post Inside Database.
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    current_year = datetime.datetime.now().year
    post = BlogPost.query.get(post_id)
    create_post_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        author=post.author,
        img_url=post.img_url,
        body=post.body
    )
    if create_post_form.validate_on_submit():
        post.title = user_input_security.script_filter(create_post_form.title.data)
        post.subtitle = user_input_security.script_filter(create_post_form.subtitle.data)
        post.author = current_user
        post.img_url = user_input_security.script_filter(create_post_form.img_url.data)
        post.body = create_post_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    else:
        return render_template("make-post.html", create_post_form=create_post_form, editing=True,
                               year=current_year, logged_in=current_user.is_authenticated)


# Create An New Post And Save It Inside Database.
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    current_year = datetime.datetime.now().year
    create_post_form = CreatePostForm()
    if create_post_form.validate_on_submit():
        new_post = BlogPost(
            title=user_input_security.script_filter(create_post_form.title.data),
            subtitle=user_input_security.script_filter(create_post_form.subtitle.data),
            author=current_user,
            img_url=user_input_security.script_filter(create_post_form.img_url.data),
            body=create_post_form.body.data,     # script_filter not used as only admin can post.
            date=datetime.datetime.now().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", create_post_form=create_post_form, editing=False,
                           year=current_year, logged_in=current_user.is_authenticated)


# Delete An Existing Post From Database.
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


# Render The "About" Section Of The Website.
@app.route("/about")
def about():
    current_year = datetime.datetime.now().year
    return render_template("about.html", year=current_year, logged_in=current_user.is_authenticated)


# Render The "Contact" Section Of The Website.
# @app.route("/contact")
# def contact():
#     current_year = datetime.datetime.now().year
#     return render_template("contact.html", year=current_year, logged_in=current_user.is_authenticated)


# Run The Server.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
