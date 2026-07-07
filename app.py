from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from database import users_dao
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-konosuba"

login_manager=LoginManager()
login_manager.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    db_user=users_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(
            id=db_user["id"],
            name=db_user["name"],
            surname=db_user["surname"],
            username=db_user["username"],
            password=db_user["password"],
            role=db_user["role"],
            profile_img=db_user["profile_img"],
            bio=db_user["bio"],
        )
    else:
        user = None
    return user

@app.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("register.html")

def check_and_save_photo(photo):
    estensioni_consentite = {"jpg", "jpeg", "png", "webp"}
    if not photo or ('.' not in photo.filename) or (photo.filename.rsplit('.', 1)[-1] not in estensioni_consentite):
        return ""
    filename_secure = secure_filename(photo.filename)
    secs = str(int(datetime.now().timestamp()))
    new_path = "static/images/profile_imgs/"+secs+"_"+filename_secure
    photo.save(new_path)
    return new_path

@app.route("/create_account", methods=["POST"])
def create_account():
    name=request.form.get("name")
    surname=request.form.get("surname")
    username=request.form.get("username")
    password=generate_password_hash(request.form.get("password"))
    role=request.form.get("role")
    profile_img=request.files["profile_img"]
    bio=request.form.get("bio")
    if users_dao.get_user_by_username(username) is not None:
        flash('A user with this username already exists.', 'danger')
        return redirect(url_for('register'))
    if role!="adventurer" and role!="master":
        flash('Please select a valid role', 'danger')
        return redirect(url_for('register'))
    if role=="master" and users_dao.get_master():
        flash('There is already a Game Master; choose another role.', 'danger')
        return redirect(url_for('register'))
    photo_path=None
    if profile_img and profile_img.filename != "":
        photo_path=check_and_save_photo(profile_img)
        if photo_path=="":
            flash('The photo format provided is incorrect. Only jpg, jpeg, png, and webp are allowed.', 'danger')
            return redirect(url_for('register'))
    users_dao.create_user(name, surname, username, password, role, photo_path, bio)
    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('login'))

@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    return render_template("login.html")

@app.route("/validation", methods=["POST"])
def validation():
    username=request.form.get("username")
    password=request.form.get("password")
    db_user=users_dao.get_user_by_username(username)
    if not db_user:
        flash("The user does not exist", "danger")
        return redirect(url_for("login"))
    elif not check_password_hash(db_user["password"], password):
        flash("The password is wrong", "danger")
        return redirect(url_for("login"))
    else:
        new=User(
            id=db_user["id"],
            name=db_user["name"],
            surname=db_user["surname"],
            username=db_user["username"],
            password=db_user["password"],
            role=db_user["role"],
            profile_img=db_user["profile_img"],
            bio=db_user["bio"],
        )
        login_user(new)
        flash("Welcome back! " + db_user["name"] + " " + db_user["surname"] + "!", "success")
    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    flash('You have been logged out.', 'info')
    logout_user()
    return redirect(url_for("home"))

@app.route("/quest_create")
@login_required
def quest_create():
    if (not current_user.is_authenticated) or current_user.role!="master":
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    return render_template("quest_create.html")