from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from database import quests_dao, reservation_dao, session_dao, users_dao
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

SIMULATE_DAY=2 # Wednesday
SIMULATE_HOUR=18
SIMULATE_MIN=25
DAYS_OF_WEEK=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
LOCATIONS=["Axel", "Kingdom of Elroad", "Arcanletia"]
DIFFICULTY=["Easy", "Medium", "Hard", "Legendary"]
TYPES=["Combact", "Exploration", "Stealth", "Magic", "Survival"]
ROLES=["Warrior", "Mage", "Healer"]
LIMITS={"Warrior": 4,  "Mage":3, "Healer":2}

app=Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-konosuba"

login_manager=LoginManager()
login_manager.init_app(app)

def assegna_foto(filtered_quests):
    for index, quest in enumerate(filtered_quests):
        quest["foto_destra"]=quest["foto_sinistra"]=""
        if (index%4==0):
            quest["foto_sinistra"]='images/home/aqua1.png'
        elif (index%4==1):
            quest["foto_destra"]='images/home/megumin.png'
        elif (index%4==2):
            quest["foto_sinistra"]='images/home/darkness.png'
        else:
            quest["foto_destra"]='images/home/kazuma.png'
    return filtered_quests

@app.route("/")
def home():
    filtered_quests=[dict(row) for row in quests_dao.get_all_quest()]
    filtered_quests=assegna_foto(filtered_quests)
    return render_template("home.html", days=DAYS_OF_WEEK, types=TYPES, difficulties=DIFFICULTY, roles=ROLES, quests=filtered_quests)

@app.route("/home_filter", methods=["POST"])
def home_filter():
    day=request.form.get("day")
    type=request.form.get("type")
    difficulty=request.form.get("difficulty")
    role=request.form.get("role")

    errors=[]
    if day!="" and day not in DAYS_OF_WEEK:
        errors.append("The day must be selected from the available options")
    day_index=DAYS_OF_WEEK.index(day) if (day and day in DAYS_OF_WEEK) else None
    if type!="" and type not in TYPES:
        errors.append("The type must be selected from the available options")
    if difficulty!="" and difficulty not in DIFFICULTY:
        errors.append("The difficulty must be selected from the available options")
    if role!="" and role not in ROLES:
        errors.append("The role must be selected from the available options")
    if len(errors)>0:
        stampa_errori(errors)
        return redirect(url_for('home'))
    filtered_quests=[dict(row) for row in quests_dao.get_filtered_quest(day_index, type, difficulty, role)]
    filtered_quests=assegna_foto(filtered_quests)
    return render_template("home.html", days=DAYS_OF_WEEK, types=TYPES, difficulties=DIFFICULTY, roles=ROLES, quests=filtered_quests, giorno=day, tipo=type, difficolta=difficulty, ruolo=role)


@login_manager.user_loader
def load_user(user_id):
    db_user=users_dao.get_user_by_id(user_id)
    if db_user is not None:
        user=User(
            id=db_user["id"],
            name=db_user["name"],
            surname=db_user["surname"],
            username=db_user["username"],
            password=db_user["password"],
            role=db_user["role"],
            profile_img=db_user["profile_img"],
            bio=db_user["bio"],)
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
    if not photo or ('.' not in photo.filename) or (photo.filename.rsplit('.', 1)[-1] not in estensioni_consentite):
        return ""
    filename_secure=secure_filename(photo.filename)
    secs=str(int(datetime.now().timestamp()))
    without_static_path=path+secs+"_"+filename_secure
    with_static_path="static/"+without_static_path
    photo.save(with_static_path)
    return without_static_path


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
        photo_path=check_and_save_photo(profile_img, "images/profile_imgs/")
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
    return int(MINUTES_IN_DAY*int(day)+int(hour)*60+int(minute))

def check_overlap(days, starts_hours, starts_minutes, duration, location, sessions):
    valid_session=[]
    overlap=False
    for index in range(min(len(days), len(starts_hours), len(starts_minutes))):
        day=DAYS_OF_WEEK.index(days[index])
        hour=int(starts_hours[index])
        minute=int(starts_minutes[index])
        current={}
        current["start"]=conversione_minuti_assoluti(day, hour, minute)
        current["end"]=current["start"]+int(duration)
        for session in sessions:
            quest=quests_dao.get_quest_by_id(session["quest_id"])
            if location==quest["location"] or location=="all":
                saved={}
                saved["start"]=conversione_minuti_assoluti(session["day"], session["hour"], session["minute"])
                saved["end"]=saved["start"]+int(quest["duration"])
                if (max(saved["start"], current["start"]))<min(saved["end"], current["end"]):
                    flash("The session of ["+DAYS_OF_WEEK[day]+" h"+str(hour)+":"+str(minute)+"] conflicts with the quest ["+quest["title"] +"]", 'danger')
                    overlap=True
                    continue
        valid_session.append((day, hour, minute))
    if location=="all":
        return overlap
    else:
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
    path_photo = check_and_save_photo(illustration, "images/illustrations/")
    if path_photo=="":
        flash("The illustration is mandatory. Only jpg, jpeg, png, and webp are allowed", 'danger')
        return redirect(url_for('quest_create'))

    sessions=session_dao.get_all_session()
    valid_sessions=check_overlap(days, starts_hours, starts_minutes, duration, location, sessions)
    if len(valid_sessions)>0:
        quest_id=quests_dao.create_quest(title, duration, location, type, difficulty, description, path_photo)
        flash("The quest has at least one valid session, so it was created correctly", 'success')
        for session in valid_sessions:
            session_dao.create_session(quest_id, session[0], session[1], session[2])
            flash("The session of ["+DAYS_OF_WEEK[session[0]]+" h"+str(session[1])+":"+str(session[2])+"] is created correctly", 'success')
    else:
        return redirect(url_for('quest_create'))
    return redirect(url_for('home'))

def split_title(title):
    b=len(title)//4
    r=len(title)%4
    return [title[i*b + min(i, r) : (i+1)*b + min(i+1, r)] for i in range(4)]

@app.route("/quest/<int:quest_id>")
def quest_detail(quest_id):
    quest_db=quests_dao.get_quest_by_id(quest_id)
    sessions_db=[dict(row) for row in session_dao.get_sessions_of_quest(quest_id)]
    for row in sessions_db:
        row["day"]=DAYS_OF_WEEK[row["day"]]
        reservations_session=reservation_dao.get_reservations_for_session(row["id"])
        for role in ROLES:
            count=0
            for reservation in reservations_session:
                if reservation["role"]==role:
                    count+=reservation["total_people"]
            row[role]=LIMITS[role]-count
    if not quest_db:
        flash("Quest non trovata", "danger")
        return redirect(url_for('home'))
    title=split_title(quest_db["title"])
    return render_template('quest_detail.html', quest=quest_db, titolo=title, sessions=sessions_db, roles=ROLES)


@app.route("/book_session", methods=["POST"])
@login_required
def book_session():
    if current_user.role!="adventurer":
        flash("To book a spot, you must be logged in as an adventurer", "danger")
        return redirect(url_for('home'))
    session_id=request.form.get("session_id")
    session=session_dao.get_session_by_id(session_id)
    if not session:
        flash("The selected session does not exist", "danger")
        return redirect(url_for('home'))
    role=request.form.get("role")
    if role not in ROLES:
        flash("The role must be selected from the available options", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    companions=request.form.getlist("companion")
    if len(companions)>2:
        flash("You are allowed to bring a maximum of two additional companions", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    reservations_session=reservation_dao.get_reservations_for_session(session_id)
    count=0
    for reservation in reservations_session:
        if reservation["role"]==role:
            count+=reservation["total_people"]
    if (LIMITS[role]-(count+len(companions)+1))<0:
        flash("You have booked more seats than are available for the category "+role, "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    
    reservations_user=reservation_dao.get_reservations_of_user(current_user.id)
    sessions_booked=[session_dao.get_session_by_id(row["session_id"]) for row in reservations_user]
    if len(reservations_user)>=3:
        flash("It is not possible to book more than 3 sessions per week", "danger")
        return redirect(url_for('quest_detail', quest_id=session["quest_id"]))
    quest=quests_dao.get_quest_by_id(session["quest_id"])
    
    if check_overlap([DAYS_OF_WEEK[session["day"]]], [session["hour"]], [session["minute"]], quest["duration"], "all", sessions_booked)==True:
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
    return redirect(url_for('home'))

def can_cancel(day, hour, minute):
    SOGLIA=8*60
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
        return redirect(url_for('profile'))
    if can_cancel(session["day"], session["hour"], session["minute"])==False:
        flash("You cannot modify or cancel this participation less than 8 hours before the session starts", "danger")
        return redirect(url_for('profile'))
    reservation_dao.delete_reservation(reservation["id"])
    flash("The booking was cancelled successfully", "success")
    return redirect(url_for('profile'))

@app.route("/profile_master")
@login_required
def profile_master():
    if current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    all_detailed_quests=quests_dao.get_all_info_of_all_quests()
    for row in all_detailed_quests:
        row["title_split"] = split_title(row["title"])
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
    # Forse si dovrebbe aggiungere la possibilità di creare anche una nuova sessione
    if current_user.role!="master":
        flash("You do not have permission to access this page", "danger")
        return redirect(url_for("home"))
    session=session_dao.get_session_by_id(session_id)
    if reservation_dao.get_reservations_for_session(session_id):
        flash("You cannot modify this session; there are already people booked", "danger")
        return redirect(url_for('profile'))
    location=request.form.get("location")
    day=request.form.get("day")
    hour=request.form.get("hour")
    minute=request.form.get("minute")
    errors=[]
    if location!="" and location not in LOCATIONS:
        errors.append("The location must be chosen from the available options")
    if day not in DAYS_OF_WEEK:
        errors.append("The day must be selected from the available options")
    hour=int(hour)
    if hour<0 or hour>23:
        errors.append("The hour can only take value between 0 and 23")
    minute=int(minute)
    if minute<0 or minute>59:
        errors.append("The minutes can only take values between 0 and 59")
    quest=quests_dao.get_quest_by_id(session["quest_id"])
    sessions=[s for s in session_dao.get_all_session() if s["id"]!=session_id]
    if len(errors) or check_overlap([day], [hour], [minute], int(quest["duration"]), "all", sessions)==True:
        stampa_errori(errors)
        return redirect(url_for('profile'))
    if location!="":
        day_index=DAYS_OF_WEEK.index(day)
        quests_dao.modify_location(location, session["quest_id"])
    session_dao.update_session(day_index, hour, minute, session_id)
    flash("The session has been successfully updated", "success")
    return redirect(url_for('profile'))

@app.route("/admin")
def admin():
    adventurers_db=[dict(row) for row in users_dao.get_all_users_for_role("adventurer")]
    user_participation_counter={user["username"]: 0 for user in adventurers_db}
    all_detailed_quests=quests_dao.get_all_info_of_all_quests()
    all_info={"total_adventurers":len(adventurers_db), "total_quests":len(all_detailed_quests), "total_sessions":0, "total_participations":0, "popular_session":None}
    total_roles={"Warrior":0, "Mage":0, "Healer":0}
    total_types={"Combact":0, "Exploration":0, "Stealth":0, "Magic":0, "Survival":0}
    popular_session={"id": -1, "total":0, "title":"", "day":-1, "hour":-1, "minute":-1}
    for quest in all_detailed_quests:
        for session in quest["sessions"]:
            all_info["total_sessions"]+=1
            all_info["total_participations"]+=session["total_booked"]
            total_types[quest["type"]]+=session["total_booked"]
            if session["total_booked"]>popular_session["total"]:
                popular_session={"id": session["id"], "total":session["total_booked"], "title":quest["title"], "day":session["day"], "hour":session["hour"], "minute":session["minute"]}
            for adventurer in session["adventurers"]:
                total_roles[adventurer["role"]]+=(len(adventurer["companions"])+1)
                user_participation_counter[adventurer["username"]]+=1
    all_info["total_roles"]=total_roles
    all_info["popular_type"]=max(total_types, key=total_types.get)
    if popular_session["id"]>=0:
        all_info["popular_session"]=session_dao.get_session_by_id(popular_session["id"])
    for user in adventurers_db:
        user["participations_count"]=user_participation_counter.get(user["username"], 0)
    return render_template("admin.html", users=adventurers_db, quests=all_detailed_quests, infos=all_info)