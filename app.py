from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from database import quests_dao, users_dao
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

SIMULATE_DAY = 3 # Wednesday
SIMULATE_HOUR = "18.34"
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
LOCATIONS = ["Axel", "Kingdom of Elroad", "Arcanletia"]
DIFFICULTY = ["Easy", "Medium", "Hard", "Legendary"]
TYPES = ["Combact", "Exploration", "Stealth", "Magic", "Survival"]
ROLES = ["Warrior", "Mage", "Healer"]

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-konosuba"

login_manager=LoginManager()
login_manager.init_app(app)


@app.route("/")
def home():
    return render_template("home.html", days=DAYS_OF_WEEK, types=TYPES, difficulties=DIFFICULTY, roles=ROLES)


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


def check_and_save_photo(photo, path="static/images/"):
    estensioni_consentite = {"jpg", "jpeg", "png", "webp"}
    if not photo or ('.' not in photo.filename) or (photo.filename.rsplit('.', 1)[-1] not in estensioni_consentite):
        return ""
    filename_secure = secure_filename(photo.filename)
    secs = str(int(datetime.now().timestamp()))
    new_path = path+secs+"_"+filename_secure
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
        flash('A user with this username already exists', 'danger')
        return redirect(url_for('register'))
    if role!="adventurer" and role!="master":
        flash('Please select a valid role', 'danger')
        return redirect(url_for('register'))
    if role=="master" and users_dao.get_master():
        flash('There is already a Game Master; choose another role', 'danger')
        return redirect(url_for('register'))
    
    photo_path=None
    if profile_img and profile_img.filename != "":
        photo_path=check_and_save_photo(profile_img, "static/images/profile_imgs/")
        if photo_path=="":
            flash('The photo format provided is incorrect. Only jpg, jpeg, png, and webp are allowed', 'danger')
            return redirect(url_for('register'))
        
    users_dao.create_user(name, surname, username, password, role, photo_path, bio)
    flash('Registration successful! Please log in', 'success')
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
    flash('You have been logged out', 'info')
    logout_user()
    return redirect(url_for("home"))


@app.route("/quest_create")
@login_required
def quest_create():
    if (not current_user.is_authenticated) or current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for('home'))
    return render_template("quest_create.html", days=DAYS_OF_WEEK, types=TYPES, difficulties=DIFFICULTY, locations=LOCATIONS)


def conversione_minuti_assoluti(day, hour, minute):
    MINUTES_IN_DAY=60*24
    return int(MINUTES_IN_DAY*int(day) + int(hour)*60 + int(minute))

def check_overlap(days, starts_hours, starts_minutes, duration, location):
    valid_session=[]
    sessions=quests_dao.get_all_session()
    for index in range(min(len(days), len(starts_hours), len(starts_minutes))):
        day=DAYS_OF_WEEK.index(days[index])
        hour=int(starts_hours[index])
        minute=int(starts_minutes[index])
        current={}
        current["start"]=conversione_minuti_assoluti(day, hour, minute)
        current["end"]=current["start"]+int(duration)
        for session in sessions:
            quest=quests_dao.get_quest_by_id(session["quest_id"])
            if location==quest["location"]:
                saved={}
                saved["start"]=conversione_minuti_assoluti(session["day"], session["hour"], session["minute"])
                saved["end"]=saved["start"]+int(quest["duration"])
                if (max(saved["start"], current["start"])) < min(saved["end"], current["end"]):
                    flash("The session of ["+DAYS_OF_WEEK[day]+" h"+str(hour)+":"+str(minute)+"] conflicts with the quest ["+quest["title"] +"]", 'danger')
                    continue
        valid_session.append((day, hour, minute))
    return valid_session

def stampa_errori(errors):
    for error in errors:
        flash(error, "danger")

@app.route("/quest_check_and_save", methods=["POST"])
@login_required
def quest_check_and_save():
    if (not current_user.is_authenticated) or current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for('home'))

    title=request.form.get("title")
    description=request.form.get("description")
    duration=request.form.get("duration")
    location=request.form.get("location")
    type=request.form.get("type")
    difficulty=request.form.get("difficulty")
    illustration=request.files["illustration"]
    days=request.form.getlist("day")
    starts_hours=request.form.getlist("hour")
    starts_minutes=request.form.getlist("minute")

    errors=[]
    if not title:
        errors.append("The title is mandatory")
    if not description:
        errors.append("The description is mandatory")
    if not duration:
        errors.append("The duration is mandatory")
    if not location:
        errors.append("The location is mandatory")
    if not type:
        errors.append("The type is mandatory")
    if not difficulty:
        errors.append("The difficulty is mandatory")
    duration=int(duration)
    if duration<=0:
        errors.append("The quest duration must be positive")
    if location not in LOCATIONS:
        errors.append("The location must be chosen from the available options")
    if type not in TYPES:
        errors.append("The type must be selected from the available options")
    if difficulty not in DIFFICULTY:
        errors.append("The difficulty must be selected from the available options")
    if len(days)==0 or len(starts_hours)==0 or len(starts_minutes)==0:
        errors.append("The quest must have at least one session")
    else:
        for day in days:
            if day not in DAYS_OF_WEEK:
                errors.append("The day must be selected from the available options")
                break
        for hour in starts_hours:
            hour=int(hour)
            if hour<0 or hour>23:
                errors.append("The hour can only take value between 0 and 23")
        for minutes in starts_minutes:
            minutes=int(minutes)
            if minutes<0 or minutes>59:
                errors.append("The minutes can only take values between 0 and 59")
    if len(errors)>0:
        stampa_errori(errors)
        return redirect(url_for('quest_create'))
    # Da mettere alla fine solo se non si vuole salvare sempre ed inutilmente altre foto
    path_photo = check_and_save_photo(illustration, "static/images/illustrations/")
    if path_photo=="":
        flash("The illustration is mandatory. Only jpg, jpeg, png, and webp are allowed", 'danegr')
        return redirect(url_for('quest_create'))

    valid_sessions=check_overlap(days, starts_hours, starts_minutes, duration, location)
    if len(valid_sessions)>0:
        quest_id=quests_dao.create_quest(title, duration, location, type, difficulty, description, path_photo)
        flash("The quest has at least one valid session, so it was created correctly", 'success')
        for session in valid_sessions:
            quests_dao.create_session(quest_id, session[0], session[1], session[2])
            flash("The session of ["+DAYS_OF_WEEK[session[0]]+" h"+str(session[1])+":"+str(session[2])+"] is created correctly", 'success')
    else:
        return redirect(url_for('quest_create'))
    return redirect(url_for('home'))