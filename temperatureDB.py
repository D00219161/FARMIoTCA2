# Mongo Database import connection
import pymongo
from pymongo import MongoClient
import dnspython

# Importing the db
from .__init__ import db

# Writing the Database Connections for home_safe
# Third collection is temp_usage


class HomeSafe(db.collection):
    __collection__ = ["temp_usage"]
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.string(4096))
    night = db.Column(db.string(4096))
    dayOfWeek = db.Column(db.string(4096))
    date = db.Column(db.Integer)
    room = db.Column(db.string(4096))
    averageTemp = db.Column(db.Double)
    hourlyUsage = db.Column(db.string(4096))
    checkedHourly = db.Column(db.string(4096))
    # User access - id, authkey, login, read & write
    authkey = db.Column(db.String(4096))
    login = db.Column(db.Integer)
    read_access = db.Column(db.Integer)
    write_access = db.Column(db.Integer)

    def __init__(self, day, night, dayOfWeek, date, room, averageTemp, hourlyUsage,
                 checkedHourly, authkey, login, read_access, write_access):
        self.day = day
        self.night = night
        self.dayOfWeek = dayOfWeek
        self.date = date
        self.room = room
        self.averageTemp = averageTemp
        self.hourlyUsage = hourlyUsage
        self.checkedHourly = checkedHourly
        self.authkey = authkey
        self.login = login
        self.read_access = read_access
        self.write_access = write_access


def delete_all():
    try:
        db.session.query(temp_usage).delete()
        db.session.commit()
        print("Delete all finished")
    except Exception as e:
        print("Failed " + str(e))
        db.session.rollback()


def get_electricity_row_if_exists(temperature_id):
    get_temperature_row = temp_usage.query.filter_by(temperature_id=temperature_id).first()
    if (get_temperature_row != None):
        return get_temperature_row
    else:
        print("Temperature data does not exist")
        return False


def add_electricity_and_login(checkedHourly, temperature_id):
    row = get_temperature_row_if_exists(temperature_id)
    if row != False:
        row.login = 1
        db.session.commit()
    else:
        print("Adding data " + checkedHourly)
        new_data = temp_usage(day, night, dayOfWeek, date, room, averageTemp, hourlyUsage,
                 checkedHourly, temperature_id, None, 1, 1)
        db.session.add(new_data)
        db.session.commit()
    print("User data" + checkedHourly + " login added")


def bool_to_int(v):
    if 'true' in str(v):
        return 1
    elif 'false' in str(v):
        return 0
    else:
        raise ValueError


def add_user_permission(temperature_id, read):
    row = get_temperature_row_if_exists(temperature_id)
    if row:
        row.read_access = bool_to_int(read)
        db.session.commit()
        print("User permission added")


def user_logout(temperature_id):
    row = get_temperature_row_if_exists(temperature_id)
    if row:
        row.login = 0
        db.session.commit()
        print("Data " + row.temperature_id + "logout updated")


def add_authkey(temperature_id, authkey):
    row = get_temperature_row_if_exists(temperature_id)
    if row:
        row.authkey = authkey
        db.session.commit()
        print("Data " + row.authkey + "authkey added")


def get_authkey(temperature_id):
    row = get_temperature_row_if_exists(temperature_id)
    if row:
        return row.authkey
    else:
        print("data with id " + temperature_id + " doesn't exist")


def get_data_access(temperature_id):
    row = get_temperature_row_if_exists(temperature_id)
    if row:
        get_temperature_row = HomeSafe.query.filter_by(temperature_id=temperature_id).first()
        read = get_temperature_row.read_access
        if read == 1:
            read = True
        else:
            read = False

        write = get_temperature_row.write_access
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
              row[n].dayOfWeek + " | " +
              str(row[n].date) + " | " +
              row[n].room + " | " +
              row[n].averageTemp + " | " +
              row[n].hourlyUsage + " | " +
              row[n].checkedEvery15Minutes + " | " +
              str(row[n].temperature_id) + " | " +
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
                                                  row[n].room, row[n].averageTemp, row[n].hourlyUsage,
                                                  row[n].checkedEvery15Minutes, row[n].temperature_id, read, write])
        print(str(row[n].id) + " | " +
              row[n].day + " | " +
              row[n].night + " | " +
              row[n].dayOfWeek + " | " +
              str(row[n].date) + " | " +
              row[n].room + " | " +
              row[n].averageTemp + " | " +
              row[n].hourlyUsage + " | " +
              row[n].checkedEvery15Minutes + " | " +
              str(row[n].temperature_id) + " | " +
              str(row[n].authkey) + " | " +
              str(row[n].login))
    return online_user_record
