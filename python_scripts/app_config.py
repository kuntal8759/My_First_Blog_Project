# Import Required Modules.
from flask import Flask
from flask_bootstrap import Bootstrap

# Create Flask "app" And Change Some Of Its Default Parameters.
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Connect Flask-Bootstrap To The Flask Server.
Bootstrap(app)
