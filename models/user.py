from db.connection import connection, cursor_wrap


class User:
    def __init__(self, user_id, name, msg, location=1, last_company_id=0):
        self.id = user_id
        self.name = name
        self.location = location
        self.region, self.city = self.set_location()
        self.last_company = ''
        self.last_company_id = last_company_id
        self.msg = msg

    @cursor_wrap
    def save(self, cursor):
        if not get_user(self.msg):
            cursor.execute(f"INSERT INTO user VALUES('{self.id}','{self.location}','{self.name}',{self.last_company_id})")
            print('User added')
            connection.commit()
        else:
            print('User already exist')

    @cursor_wrap
    def update_location_by_region(self, cursor):
        cursor.execute(f"SELECT id FROM location WHERE region='{self.region}'")
        self.location = cursor.fetchall()[0][0]
        cursor.execute(f"UPDATE user SET location={self.location} WHERE id={self.id}")
        print('Region location updated')
        connection.commit()

    @cursor_wrap
    def update_last_company(self, cursor):
        cursor.execute(f"SELECT id FROM location WHERE region='{self.region}' and city='{self.city}'")
        self.location = cursor.fetchall()[0][0]
        cursor.execute(f"UPDATE user SET last_company={self.last_company_id} WHERE id={self.id}")
        print('Last company updated')
        connection.commit()

    @cursor_wrap
    def update_location(self, cursor):
        cursor.execute(f"SELECT id FROM location WHERE region='{self.region}' and city='{self.city}'")
        self.location = cursor.fetchall()[0][0]
        cursor.execute(f"UPDATE user SET location={self.location} WHERE id={self.id}")
        print('Location updated')
        connection.commit()

    @cursor_wrap
    def set_location(self, cursor):
        cursor.execute(f"SELECT region, city FROM location WHERE id='{self.location}'")
        res = cursor.fetchall()
        if res:
            return res[0]
        else:
            return 'Киев', 'Киев'


@cursor_wrap
def get_user(msg, cursor):
        try:
            cursor.execute(f'SELECT * FROM user WHERE id={msg.from_user.id}')
            res = cursor.fetchall()
            if res:
                res = res[0]
                return User(user_id=res[0], name=res[2], location=res[1], msg=msg, last_company_id=res[3])
            else:
                return False
        except AttributeError:
            return msg


@cursor_wrap
def get_name_by_id(uid, cursor):
    cursor.execute(f'SELECT name FROM user WHERE id={uid}')
    return cursor.fetchall()[0][0]


def get_user_wrap(func):
    def wrapper(msg):
        user = get_user(msg)
        if user:
            func(user)
        else:
            user = User(user_id=msg.from_user.id, name=msg.from_user.first_name, msg=msg)
            user.save()
            func(user)
    return wrapper
