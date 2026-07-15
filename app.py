from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from database import quests_dao, reservation_dao, session_dao, users_dao
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

SIMULATE_DAY=2
SIMULATE_HOUR=14
SIMULATE_MIN=30
DAYS_OF_WEEK=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
LOCATIONS=["Axel", "Kingdom of Elroad", "Arcanletia"]
DIFFICULTY=["Easy", "Medium", "Hard", "Legendary"]
TYPES=["Combact", "Exploration", "Stealth", "Magic", "Survival"]
ROLES=["Warrior", "Mage", "Healer"]
LIMITS={"Warrior": 4,  "Mage":3, "Healer":2}

app=Flask(__name__)
app.config["SECRET_KEY"]="KoNoSuBa-secret-key"

login_manager=LoginManager()
login_manager.init_app(app)

def assegna_foto(filtered_quests):
    for index, quest in enumerate(filtered_quests):
        quest["foto_destra"]=quest["foto_sinistra"]=""
        if (index%4==0):
            quest["foto_sinistra"]='images/home/aqua.png'
        elif (index%4==1):
            quest["foto_destra"]='images/home/megumin.png'
        elif (index%4==2):
            quest["foto_sinistra"]='images/home/darkness.png'
        else:
            quest["foto_destra"]='images/home/kazuma.png'
    return filtered_quests

@app.route("/")
def home():
    filtered_quests=assegna_foto([dict(row) for row in quests_dao.get_all_quest()])
    return render_template("home.html", days=DAYS_OF_WEEK, types=TYPES, difficulties=DIFFICULTY, roles=ROLES, quests=filtered_quests)

@app.route("/home_filter", methods=["POST"])
def home_filter():
    day=request.form.get("day")
    type=request.form.get("type")
    difficulty=request.form.get("difficulty")
    role=request.form.get("role")
    if day!="" and day not in DAYS_OF_WEEK:
        flash("The day is mandatory and must be selected from the available options", "danger")
        return redirect(url_for('home'))
    day_index=DAYS_OF_WEEK.index(day) if (day and day in DAYS_OF_WEEK) else None
    if type!="" and type not in TYPES:
        flash("The type is mandatory and must be selected from the available options", "danger")
        return redirect(url_for('home'))
    if difficulty!="" and difficulty not in DIFFICULTY:
        flash("The difficulty is mandatory and must be selected from the available options", "danger")
        return redirect(url_for('home'))
    if role!="" and role not in ROLES:
        flash("The role is mandatory and must be selected from the available options", "danger")
        return redirect(url_for('home'))
    
    filtered_quests=assegna_foto([dict(row) for row in quests_dao.get_filtered_quest(day_index, type, difficulty, role)])
    return render_template("home.html", days=DAYS_OF_WEEK, types=TYPES, difficulties=DIFFICULTY, roles=ROLES, quests=filtered_quests, giorno=day, tipo=type, difficolta=difficulty, ruolo=role)

@login_manager.user_loader
def load_user(user_id):
    db_user=users_dao.get_user_by_id(user_id)
    if db_user is not None:
        user=User(
            id=db_user["id"], name=db_user["name"], surname=db_user["surname"],
            username=db_user["username"], password=db_user["password"],
            role=db_user["role"], profile_img=db_user["profile_img"], bio=db_user["bio"],)
    else:
        user=None
    return user

@app.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("register.html")

def check_and_save_photo(photo, path):
    estensioni_consentite={"jpg", "jpeg", "png", "webp"}
    if not photo or ('.' not in photo.filename) or (photo.filename.rsplit('.')[-1] not in estensioni_consentite):
        return ""
    secs=str(int(datetime.now().timestamp()))
    path_db=path+secs+"_"+secure_filename(photo.filename)
    photo.save("static/"+path_db)
    return path_db

@app.route("/create_account", methods=["POST"])
def create_account():
    name=request.form.get("name")
    surname=request.form.get("surname")
    username=request.form.get("username").strip()
    password=generate_password_hash(request.form.get("password"))
    profile_img=request.files["profile_img"]
    bio=request.form.get("bio")
    if username is None or username=="":
        flash("The username is mandatory", "danger")
        return redirect(url_for('register'))
    if users_dao.get_user_by_username(username) is not None:
        flash('A user with this username already exists', 'danger')
        return redirect(url_for('register'))
    photo_path=None
    if profile_img and profile_img.filename!="":
        photo_path=check_and_save_photo(profile_img, "images/profile_imgs/")
        if photo_path=="":
            flash('The photo format provided is incorrect. Only jpg, jpeg, png, and webp are allowed', 'danger')
            return redirect(url_for('register'))
    
    users_dao.create_user(name, surname, username, password, "adventurer", photo_path, bio)
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
        new=User(id=db_user["id"], name=db_user["name"], surname=db_user["surname"],
            username=db_user["username"], password=db_user["password"],
            role=db_user["role"], profile_img=db_user["profile_img"], bio=db_user["bio"],)
        login_user(new)
        flash("Welcome back! "+db_user["name"]+" "+db_user["surname"]+"!", "success")
    return redirect(url_for("profile"))

@app.route("/logout")
@login_required
def logout():
    flash('You have been logged out', 'info')
    logout_user()
    return redirect(url_for("home"))

@app.route("/quest_create")
@login_required
def quest_create():
    if current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for('home'))
    return render_template("quest_create.html", days=DAYS_OF_WEEK, types=TYPES, difficulties=DIFFICULTY, locations=LOCATIONS)

def conversione_minuti_assoluti(day, hour, minute):
    return int((60*24)*int(day)+int(hour)*60+int(minute))

def check_overlap(day, hour, minute, duration, location, sessions):
    day=DAYS_OF_WEEK.index(day)
    hour=int(hour)
    minute=int(minute)
    current={"start":conversione_minuti_assoluti(day, hour, minute)}
    current["end"]=current["start"]+int(duration)
    for session in sessions:
        quest=quests_dao.get_quest_by_id(session["quest_id"])
        if location==session["location"] or location=="all":
            saved={"start": conversione_minuti_assoluti(session["day"], session["hour"], session["minute"])}
            saved["end"]=saved["start"]+int(quest["duration"])
            if (max(saved["start"], current["start"]))<min(saved["end"], current["end"]):
                flash("The session of ["+DAYS_OF_WEEK[day]+" h"+str(hour)+":"+str(minute)+"] conflicts with the quest ["+quest["title"] +"]", 'danger')
                return True
    return False

def validate_and_create_session(quest_id, location, day, hour, minute, duration, exist_sessions, flag_mod=False):
    if not location or location not in LOCATIONS:
        flash("The location must be chosen from the available options", "danger")
        return False
    if day not in DAYS_OF_WEEK:
        flash("The day must be selected from the available options", "danger")
        return False
    if int(hour)<0 or int(hour)>23:
        flash("The hour can only take value between 0 and 23", "danger")
        return False
    if int(minute)<0 or int(minute)>59:
        flash("The minutes can only take values between 0 and 59", "danger")
        return False
    if check_overlap(day, hour, minute, duration, location, exist_sessions)==True:
        return False
    session_dao.create_session(quest_id, location, DAYS_OF_WEEK.index(day), int(hour), int(minute))
    if flag_mod==False:
        flash("The session of ["+location+":"+DAYS_OF_WEEK[day]+" h"+str(hour)+":"+str(minute)+"] is created correctly", 'success')
    return True

@app.route("/quest_check_and_save", methods=["POST"])
@login_required
def quest_check_and_save():
    if (not current_user.is_authenticated) or current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for('home'))
    title=request.form.get("title")
    description=request.form.get("description")
    duration=request.form.get("duration")
    type=request.form.get("type")
    difficulty=request.form.get("difficulty")
    illustration=request.files["illustration"]
    days=request.form.getlist("day")
    starts_hours=request.form.getlist("hour")
    starts_minutes=request.form.getlist("minute")
    locations=request.form.getlist("location")
    
    if not title:
        flash("The title is mandatory", "danger")
        return redirect(url_for('quest_create'))
    if not description:
        flash("The description is mandatory", "danger")
        return redirect(url_for('quest_create'))
    if not duration or int(duration)<=0:
        flash("The duration is mandatory and must be positive", "danger")
        return redirect(url_for('quest_create'))
    duration=int(duration)
    if not type or type not in TYPES:
        flash("The type is mandatory and must be selected from the available options", "danger")
        return redirect(url_for('quest_create'))
    if not difficulty or difficulty not in DIFFICULTY:
        flash("The difficulty is mandatory and must be selected from the available options", "danger")
        return redirect(url_for('quest_create'))
    path_photo=check_and_save_photo(illustration, "images/illustrations/")
    if path_photo=="":
        flash("The illustration is mandatory. Only jpg, jpeg, png, and webp are allowed", 'danger')
        return redirect(url_for('quest_create'))
    
    quest_id=quests_dao.create_quest(title, duration, type, difficulty, description, path_photo)
    flash("The quest was created correctly", 'success')
    
    valid_sessions=[]
    exist_sessions=session_dao.get_all_session()
    for index in range(min(len(days), len(starts_hours), len(starts_minutes), len(locations))):
        if validate_and_create_session(quest_id, locations[index], days[index], starts_hours[index], starts_minutes[index], duration, exist_sessions):
            valid_sessions.append((DAYS_OF_WEEK.index(days[index]), int(starts_hours[index]), int(starts_minutes[index]), locations[index]))
            exist_sessions.append({"quest_id": quest_id, "location": locations[index], "day": DAYS_OF_WEEK.index(days[index]), "hour": int(starts_hours[index]), "minute": int(starts_minutes[index]) })
    if len(valid_sessions)==0:
        flash("All the entered sessions overlap with other existing sessions so no sessions for quest ["+title+"] was created", "danger")  
    return redirect(url_for('profile'))

def split_title(title):
    base_size=len(title)//4
    remainder=len(title)%4
    parts=[]
    start=0
    for i in range(4):
        size=base_size+(1 if i < remainder else 0)
        parts.append(title[start:start+size])
        start=start+size
    return parts

@app.route("/quest/<int:quest_id>")
def quest_detail(quest_id):
    quest_db=quests_dao.get_quest_by_id(quest_id)
    if not quest_db:
        flash("Quest not found", "danger")
        return redirect(url_for('home'))
    sessions_db=[dict(row) for row in session_dao.get_sessions_of_quest(quest_id)]
    for session in sessions_db:
        session["can_cancel"]=can_cancel(session["day"], session["hour"], session["minute"])
        session["is_past"]=not can_cancel(session["day"], session["hour"], session["minute"], 0)
        session["day"]=DAYS_OF_WEEK[session["day"]]
        reservations_session=reservation_dao.get_reservations_for_session(session["id"])
        for role in ROLES:
            session[role]=LIMITS[role]
            for reservation in reservations_session:
                if reservation["role"]==role:
                    session[role]-=reservation["total_people"]
    reservations_user_db=[]
    if current_user.is_authenticated:
        reservations_user_db=[reservation["session_id"] for reservation in reservation_dao.get_reservations_of_user(current_user.id)]
    return render_template('quest_detail.html', quest=quest_db, titolo=split_title(quest_db["title"]), sessions=sessions_db, roles=ROLES, reservations_user=reservations_user_db)

@app.route("/book_session", methods=["POST"])
@login_required
def book_session():
    if current_user.role!="adventurer":
        flash("To book a spot you must be logged in as an adventurer", "danger")
        return redirect(url_for('home'))
    session_id=request.form.get("session_id")
    role=request.form.get("role")
    companions=[comp.strip() for comp in request.form.getlist("companion") if comp.strip()]
    session=session_dao.get_session_by_id(session_id)
    
    if not session:
        flash("The selected session does not exist", "danger")
        return redirect(url_for('home')) 
    if not can_cancel(session["day"], session["hour"], session["minute"], 0):
        flash("You cannot join a session that has already passed", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    if role not in ROLES:
        flash("The role must be selected from the available options", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    if len(companions)>1:
        flash("You are allowed to bring a maximum of one additional companions", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    reservations_user=reservation_dao.get_reservations_of_user(current_user.id)
    if len(reservations_user)>=3:
        flash("It is not possible to book more than 3 sessions per week", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    reservations_session=reservation_dao.get_reservations_for_session(session_id)
    count=0
    for reservation in reservations_session:
        if reservation["role"]==role:
            count+=reservation["total_people"]
    if (LIMITS[role]-(count+(len(companions)+1)))<0:
        flash("You have booked more seats than are available for the category "+role, "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    quest=quests_dao.get_quest_by_id(session["quest_id"])
    sessions_booked=[session_dao.get_session_by_id(reservation_db["session_id"]) for reservation_db in reservations_user]
    if check_overlap(DAYS_OF_WEEK[session["day"]], session["hour"], session["minute"], quest["duration"], "all", sessions_booked)==True:
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    
    reservation_id=reservation_dao.create_reservation(current_user.id, session_id, role, int(len(companions))+1)
    for companion in companions:
        reservation_dao.add_companions(reservation_id, companion)
    flash("The booking was made successfully", "success")
    return redirect(url_for('profile'))

@app.route("/profile")
@login_required
def profile():
    if current_user.role=="adventurer":
        return redirect(url_for('profile_adventurer'))
    elif current_user.role=="master":
        return redirect(url_for('profile_master'))
    elif current_user.role=="admin":
        return redirect(url_for('admin'))
    return redirect(url_for('home'))

def can_cancel(day, hour, minute, SOGLIA=8*60):
    current_simulated=conversione_minuti_assoluti(SIMULATE_DAY, SIMULATE_HOUR, SIMULATE_MIN)
    session=conversione_minuti_assoluti(day, hour, minute)
    return (session-current_simulated)>SOGLIA

@app.route("/profile_adventurer")
@login_required
def profile_adventurer():
    if current_user.role!="adventurer":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    user_quests_dict=reservation_dao.get_detailed_adventurer_quests(current_user.id)
    for quest in user_quests_dict:
        for session in quest["sessions"]:
            session["is_past"]=not can_cancel(session["day"], session["hour"], session["minute"],0)
            session["can_cancel"]=can_cancel(session["day"], session["hour"], session["minute"])
            session["day"]=DAYS_OF_WEEK[session["day"]]
    return render_template("profile_adventurer.html", quests=user_quests_dict)

@app.route("/cancel_reservation/<int:session_id>")
@login_required
def cancel_reservation(session_id):
    if current_user.role!="adventurer":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    session=session_dao.get_session_by_id(session_id)
    reservation=reservation_dao.get_reservation_by_session_for_user(current_user.id, session_id)
    if not reservation:
        flash("The selected reservation does not exist", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    if can_cancel(session["day"], session["hour"], session["minute"])==False:
        flash("You cannot modify or cancel a booking less than 8 hours before the start of the session", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    reservation_dao.delete_reservation(reservation["id"])
    flash("The partecipation was cancelled successfully", "success")
    return redirect(url_for('quest_detail', quest_id=session["quest_id"]))

@app.route("/profile_master")
@login_required
def profile_master():
    if current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    all_detailed_quests=quests_dao.get_all_info_of_all_quests()
    for quest in all_detailed_quests:
        quest["title_split"]=split_title(quest["title"])
    return render_template("profile_master.html", quests=all_detailed_quests, days=DAYS_OF_WEEK, locations=LOCATIONS)

@app.route("/cancel_session/<int:session_id>")
@login_required
def cancel_session(session_id):
    if current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    if reservation_dao.get_reservations_for_session(session_id):
        flash("You cannot cancel this session; there are already people booked", "danger")
        return redirect(url_for('profile'))
    session_dao.delete_session(session_id)
    flash("The session was cancelled successfully", "success")
    return redirect(url_for('profile'))

@app.route("/modify_session/<int:session_id>", methods=["POST"])
@login_required
def modify_session(session_id):
    if current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    session=session_dao.get_session_by_id(session_id)
    if not session:
        flash("The selected session does not exist", "danger")
        return redirect(url_for('profile'))
    if reservation_dao.get_reservations_for_session(session_id):
        flash("You cannot modify this session; there are already people booked", "danger")
        return redirect(url_for('profile'))
    location=request.form.get("location")
    day=request.form.get("day")
    hour=request.form.get("hour")
    minute=request.form.get("minute")
    
    quest=quests_dao.get_quest_by_id(session["quest_id"])
    exist_sessions=[ses for ses in session_dao.get_all_session() if ses["id"]!=session_id]
    if validate_and_create_session(quest["id"], location, day, hour, minute, int(quest["duration"]), exist_sessions, True)==False:
        flash("It was not possible to modify the session as requested", "danger")
        return redirect(url_for('profile'))
    session_dao.delete_session(session_id)
    flash("The session has been successfully updated", "success")
    return redirect(url_for('profile'))

@app.route("/create_session/<int:quest_id>", methods=["POST"])
@login_required
def create_session(quest_id):
    if current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    quest=quests_dao.get_quest_by_id(quest_id)
    if not quest:
        flash("The selected quest does not exist", "danger")
        return redirect(url_for('profile'))
    location=request.form.get("location")
    day=request.form.get("day")
    hour=request.form.get("hour")
    minute=request.form.get("minute")
    if validate_and_create_session(quest_id, location, day, hour, minute, int(quest["duration"]), session_dao.get_all_session())==False:
        return redirect(url_for('profile'))
    return redirect(url_for('profile'))

@app.route("/admin")
@login_required
def admin():
    if current_user.role!="admin":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    adventurers_db=users_dao.get_adventures_with_number_of_participation()
    all_detailed_quests=quests_dao.get_all_info_of_all_quests()
    general_infos=quests_dao.get_admin_stats()
    for session in general_infos["popular_sessions"]:
        session["title"]=split_title(session["title"])
    return render_template("admin.html", users=adventurers_db, quests=all_detailed_quests, infos=general_infos)