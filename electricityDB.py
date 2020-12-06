# Mongo Database import connection
import pymongo
from pymongo import MongoClient
import dnspython

# Importing the db
from .__init__ import db

# Writing the Database Connections for home_safe
# Second collection is electricity_usage


class HomeSafe(db.collection):
    __collection__ = ["electricity_usage"]
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.string(4096))
    night = db.Column(db.string(4096))
    dayOfWeek = db.Column(db.string(4096))
    date = db.Column(db.Integer)
    rural = db.Column(db.string(4096))
    urban = db.Column(db.string(4096))
    hourlyUsage = db.Column(db.string(4096))
    checkedEvery15Minutes = db.Column(db.string(4096))
    # User access - id, authkey, login, read & write
    authkey = db.Column(db.String(4096))
    login = db.Column(db.Integer)
    read_access = db.Column(db.Integer)
    write_access = db.Column(db.Integer)

    def __init__(self, day, night, dayOfWeek, date, rural, urban, hourlyUsage,
                 checkedEvery15Minutes, authkey, login, read_access, write_access):
        self.day = day
        self.night = night
        self.dayOfWeek = dayOfWeek
        self.date = date
        self.rural = rural
        self.urban = urban
        self.hourlyUsage = hourlyUsage
        self.checkedEvery15Minutes = checkedEvery15Minutes
        self.authkey = authkey
        self.login = login
        self.read_access = read_access
        self.write_access = write_access


def delete_all():
    try:
        db.session.query(electricity_usage).delete()
        db.session.commit()
        print("Delete all finished")
    except Exception as e:
        print("Failed " + str(e))
        db.session.rollback()


def get_electricity_row_if_exists(electricity_id):
    get_electricity_row = electricity_usage.query.filter_by(electricity_id=electricity_id).first()
    if (get_electricity_row != None):
        return get_electricity_row
    else:
        print("Electricity data does not exist")
        return False


def add_electricity_and_login(checkedEvery15Minutes, electricity_id):
    row = get_electricity_row_if_exists(electricity_id)
    if row != False:
        row.login = 1
        db.session.commit()
    else:
        print("Adding data " + checkedEvery15Minutes)
        new_data = electricity_usage(day, night, dayOfWeek, date, rural, urban, hourlyUsage,
                 checkedEvery15Minutes, electricity_id, None, 1, 1)
        db.session.add(new_data)
        db.session.commit()
    print("User data" + checkedEvery15Minutes + " login added")


def bool_to_int(v):
    if 'true' in str(v):
        return 1
    elif 'false' in str(v):
        return 0
    else:
        raise ValueError


def add_user_permission(electricity_id, read):
    row = get_user_row_if_exists(electricity_id)
    if row:
        row.read_access = bool_to_int(read)
        db.session.commit()
        print("User permission added")


def user_logout(electricity_id):
    row = get_electricity_row_if_exists(electricity_id)
    if row:
        row.login = 0
        db.session.commit()
        print("Data " + row.electricity_id + "logout updated")


def add_authkey(user_id, authkey):
    row = get_electricity_row_if_exists(electricity_id)
    if row:
        row.authkey = authkey
        db.session.commit()
        print("Data " + row.authkey + "authkey added")


def get_authkey(electricity_id):
    row = get_electricity_row_if_exists(electricity_id)
    if row:
        return row.authkey
    else:
        print("data with id " + electricity_id + " doesn't exist")


def get_data_access(electricity_id):
    row = get_electricity_row_if_exists(electricity_id)
    if row:
        get_electricity_row = HomeSafe.query.filter_by(electricity_id=electricity_id).first()
        read = get_electricity_row.read_access
        if read == 1:
            read = True
        else:
            read = False

        write = get_electricity_row.write_access
        if write == 1:
            write = True
        else:
            write = False
    return read, write


def view_all():
    row = HomeSafe.query.all()
    for n in range(0, len(row)):
        print(str(row[n].id) + " | " +
              row[n].day + " | " +
              row[n].night + " | " +
              str(row[n].dayOfWeek) + " | " +
              row[n].date + " | " +
              row[n].rural + " | " +
              row[n].urban + " | " +
              row[n].hourlyUsage + " | " +
              row[n].checkedEvery15Minutes + " | " +
              str(row[n].electricity_id) + " | " +
              str(row[n].authkey) + " | " +
              str(row[n].login))


def get_all_logged_in_data():
    row = HomeSafe.query.filter_by(login=1).all()
    online_user_record = {"data_record": []}
    print("LoggedIn Data:")
    for n in range(0, len(row)):
        if row[n].read_access:
            read = "checked"
        else:
            read = "unchecked"
        if row[n].write_access:
            write = "checked"
        else:
            read = "unchecked"
        online_user_record["user_record"].append([row[n].day, row[n].night, row[n].dayOfWeek, row[n].date,
                                                  row[n].rural, row[n].urban, row[n].hourlyUsage,
                                                  row[n].checkedEvery15Minutes, row[n].electricity_id, read, write])
        print(str(row[n].id) + " | " +
              row[n].day + " | " +
              row[n].night + " | " +
              str(row[n].dayOfWeek) + " | " +
              row[n].date + " | " +
              row[n].rural + " | " +
              row[n].urban + " | " +
              row[n].hourlyUsage + " | " +
              row[n].checkedEvery15Minutes + " | " +
              str(row[n].electricity_id) + " | " +
              str(row[n].authkey) + " | " +
              str(row[n].login))
    return online_user_record
