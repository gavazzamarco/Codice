from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from database import users_dao
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-konosuba"

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    db_user = users_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(
            id=db_user["id"],
            name=db_user["name"],
            surname=db_user["surname"],
            username=db_user["username"],
            password=db_user["password"],
            role=db_user["role"],
            profile_img=db_user["profile_img"],
        )
    else:
        user = None
    return user

@app.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("register.html")

@app.route("/create_account", methods=["POST"])
def create_account():
    name = request.form.get("name")
    surname = request.form.get("surname")
    username = request.form.get("username")
    password = generate_password_hash(request.form.get("password"))
    role = request.form.get("role")
    profile_img = request.form.get("profile_img")
    if users_dao.get_user_by_username(username):
        flash('A user with this username already exists.', 'danger')
        redirect(url_for('register'))
    users_dao.create_user(name, surname, username, password, role, profile_img)
    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('login'))

@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    return render_template("login.html")

@app.route("/validation", methods=["POST"])
def validation():
    username = request.form.get("username")
    password = request.form.get("password")
    db_user = users_dao.get_user_by_username(username)
    if not db_user:
        flash("The user does not exist", "danger")
        return redirect(url_for("login"))
    elif not check_password_hash(db_user["password"], password):
        flash("The password is wrong", "danger")
        return redirect(url_for("login"))
    else:
        new = User(
            id=db_user["id"],
            name=db_user["name"],
            surname=db_user["surname"],
            username=db_user["username"],
            password=db_user["password"],
            role=db_user["role"],
            profile_img=db_user["profile_img"],
        )
        login_user(new)
        flash("Welcome back! " + db_user["name"] + " " + db_user["surname"] + "!", "success")
    return redirect(url_for("home"))