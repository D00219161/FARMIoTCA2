# Mongo Database import connection
import pymongo
from pymongo import MongoClient
import dnspython

# Importing the db
from .__init__ import db

# Writing the Database Connections for home_safe
# First collection is users


class HomeSafe(db.collectio):
    __collection__ = db["users"]
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.string(4096))
    surname = db.Column(db.string(4096))
    password = db.Column(db.string(4096))
    phoneNumber = db.Column(db.Integer)
    emailAddress = db.Column(db.string(4096))
    address = db.Column(db.string(4096))
    postCode = db.Column(db.string(4096))
    dateOfBirth = db.Column(db.string(4096))
    gender = db.Column(db.string(4096))
    # User access - id, authkey, login & read
    user_id = db.Column(db.Integer)
    authkey = db.Column(db.String(4096))
    login = db.Column(db.Integer)
    read_access = db.Column(db.Integer)

    def __init__(self, firstname, surname, password, phoneNumber, emailAddress, address, postCode,
                 dateOfBirth, gender, user_id, authkey, login, read_access):
        self.firstname = firstname
        self.surname = surname
        self.password = password
        self.phoneNumber = phoneNumber
        self.emailAddress = emailAddress
        self.address = address
        self.postCode = postCode
        self.dateOfBirth = dateOfBirth
        self.gender = gender
        self.user_id = user_id
        self.authkey = authkey
        self.login = login
        self.read_access = read_access


def delete_all():
    try:
        db.session.query(HomeSafe).delete()
        db.session.commit()
        print("Delete all finished")
    except Exception as e:
        print("Failed " + str(e))
        db.session.rollback()


def get_user_row_if_exists(user_id):
    get_user_row = HomeSafe.query.filter_by(user_id=user_id).first()
    if (get_user_row != None):
        return get_user_row
    else:
        print("User does not exist")
        return False


def add_user_and_login(firstname, user_id):
    row = get_user_row_if_exists(user_id)
    if row != False:
        row.login = 1
        db.session.commit()
    else:
        print("Adding user " + firstname)
        new_user = HomeSafe(firstname, firstname, surname, password, phoneNumber, emailAddress, address, postCode,
                            dateOfBirth, gender, user_id, None, 1, 0)
        db.session.add(new_user)
        db.session.commit()
    print("User " + firstname + " login added")


def bool_to_int(v):
    if 'true' in str(v):
        return 1
    elif 'false' in str(v):
        return 0
    else:
        raise ValueError


def add_user_permission(user_id, read):
    row = get_user_row_if_exists(user_id)
    if row:
        row.read_access = bool_to_int(read)
        db.session.commit()
        print("User permission added")


def user_logout(user_id):
    row = get_user_row_if_exists(user_id)
    if row:
        row.login = 0
        db.session.commit()
        print("User " + row.firstname + "logout updated")


def add_authkey(user_id, authkey):
    row = get_user_row_if_exists(user_id)
    if row:
        row.authkey = authkey
        db.session.commit()
        print("User " + row.authkey + "authkey added")


def get_authkey(user_id):
    row = get_user_row_if_exists(user_id)
    if row:
        return row.authkey
    else:
        print("User with id " + user_id + " doesn't exist")


def get_user_access(user_id):
    row = get_user_row_if_exists(user_id)
    if row:
        get_user_row = HomeSafe.query.filter_by(user_id=user_id).first()
        read = get_user_row.read_access
        if read == 1:
            read = True
        else:
            read = False
    return read


def view_all():
    row = HomeSafe.query.all()
    for n in range(0, len(row)):
        print(str(row[n].id) + " | " +
              row[n].firstname + " | " +
              row[n].surname + " | " +
              row[n].password + " | " +
              str(row[n].phoneNumber) + " | " +
              row[n].emailAddress + " | " +
              row[n].address + " | " +
              row[n].postCode + " | " +
              row[n].dateOfBirth + " | " +
              row[n].gender + " | " +
              str(row[n].user_id) + " | " +
              str(row[n].authkey) + " | " +
              str(row[n].login))


def get_all_logged_in_users():
    row = HomeSafe.query.filter_by(login=1).all()
    online_user_record = {"user_record": []}
    print("LoggedIn Users:")
    for n in range(0, len(row)):
        if row[n].read_access:
            read = "checked"
        else:
            read = "unchecked"
        online_user_record["user_record"].append([row[n].firstname, row[n].surname, row[n].password, row[n].phoneNumbe,
                                                  row[n].emailAddress, row[n].address, row[n].postCode,
                                                  row[n].dateOfBirth, row[n].gender, row[n].user_id, read])
        print(str(row[n].id) + " | " +
              row[n].firstname + " | " +
              row[n].surname + " | " +
              row[n].password + " | " +
              str(row[n].phoneNumber) + " | " +
              row[n].emailAddress + " | " +
              row[n].address + " | " +
              row[n].postCode + " | " +
              row[n].dateOfBirth + " | " +
              row[n].gender + " | " +
              str(row[n].user_id) + " | " +
              str(row[n].authkey) + " | " +
              str(row[n].login))
    return online_user_record
