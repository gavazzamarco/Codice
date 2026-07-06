from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from models import User
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-konosuba"

# login_manager = LoginManager()
# login_manager.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")