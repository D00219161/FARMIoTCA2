from flask import Flask, render_template, url_for, session, flash
import json, string, random, hashlib

# Mongo Database import connection
import pymongo
from pymongo import MongoClient, dnspython

from functools import wraps

from werkzeug.utils import redirect

app = Flask(__name__)

# Mongo DB Connection
cluster = MongoClient("mongodb+srv://Roisin:DFM5CauDv8K9tXpY@cluster0.b528o.mongodb.net/home_safe?retryWrites=true&w=majority")
# Mongo Database Config
db = cluster["home_safe"]
collection = db["electricity_usage"], db["temp_usage"], db["users"]

db = cluster(app)

from . import homesafeDB, PB

alive = 0
data = {}

# Grant read and write access to the authkey "SD3b-Raspberry-Pi" - More than One Pi
PB.grant_access("Homesafe-Matthew-Raspberry-Pi", True, True)  # Matthew's Pi Connection to read & write
PB.grant_access("Homesafe-Finbar-Raspberry-Pi", True, True)  # Finbar's Pi Connection to read & write


@app.route("/login")
def index():
    return render_template("index.html")


def LoginRequired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            if session['logged_in']:
                return f(*args, **kwargs)
        flash("Please login first")
        return redirect(url_for('login'))

    return wrapper


@app.route("/main")
@LoginRequired
def main():
    flash(session["user"])
    homesafeDB.add_user_and_login(session['user'], int(session['user_id']))
    homesafeDB.view_all()
    return render_template("index.html", user_id=session['user_id'], online_users=homesafeDB.get_all_logged_in_users())


def clear_session():
    session['logged_in'] = None
    session['user'] = None
    session['user_id'] = None


@app.route("/")
def login():
    clear_session()
    return render_template("login.html")


@app.route("/logout")
def logout():
    homesafeDB.user_logout(session['user_id'])
    homesafeDB.view_all()
    clear_session()
    flash("You just logged out")
    return redirect(url_for("login"))


@app.route("/keep_alive", methods=["GET"])
def keep_alive():
    global alive, data
    alive += 1
    keep_alive_count = str(alive)
    data['keep_alive'] = keep_alive_count
    parsed_json = json.dumps(data)
    print(str(parsed_json))
    return str(parsed_json)


def str_to_bool(s):
    if 'true' in str(s):
        return True
    elif 'false' in str(s):
        return False
    else:
        raise ValueError


@app.route("/grant-<user_id>-<read>-<write>", methods=["POST", "GET"])
def grant_access(user_id, read, write):
    if int(session['user_id']) == 1884560171685373:
        print("Granting " + user_id + " read: " + read + " write: " + write + " permission")
        # store user read/write permissions into the database
        homesafeDB.add_user_permission(user_id, read, write)
        auth_key = homesafeDB.get_authkey(user_id)
        # grant PubNub read/write access
        PB.grant_access(auth_key, str_to_bool(read), str_to_bool(write))
    else:
        print("Who are you?")
        return json.dumps({"access":"denied"})
    return json.dumps({"access":"granted"})


# Salting
def salt(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Creating auth key for user
def create_auth_key():
    s = salt(10)
    hashing = hashlib.sha256((str(session['user_id']) + s).encode('utf-8'))
    return hashing.hexdigest()


@app.route("/get_auth_Key", methods=["POST", "GET"])
def get_auth_key():
    print("Creating authkey for " + session['user'])
    auth_key = create_auth_key()
    homesafeDB.add_authkey(int(session['user_id']), auth_key)
    (read, write) = homesafeDB.get_user_access(int(session['user_id']))
    # Use PubNub to grant these privileges to this user
    PB.grant_access(auth_key, read, write)
    auth_response = {"authKey":auth_key, "cipherKey":PB.cipherKey}
    json_response = json.dumps(auth_response)
    return str(json_response)
    return str("authkey")


if __name__ == "__main__":
    app.run()
