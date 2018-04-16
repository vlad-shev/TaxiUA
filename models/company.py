from db.connection import connection, cursor_wrap


class Company:
    def __init__(self, location, name):
        self.location = location
        self.name = name
        self.description = ''
        self.phone = ''

    @cursor_wrap
    def save(self, cursor):
        if not self.get_id():
            cursor.execute(
                f"INSERT INTO company VALUES(NULL,{self.location},'{self.name}','{self.description}','{self.phone}')")
            print('Company added')
            connection.commit()
        else:
            print('Company already exist')

    @cursor_wrap
    def get_id(self, cursor):
        cursor.execute(f"SELECT id FROM company WHERE location='{self.location}' and name='{self.name}'")
        res = cursor.fetchall()
        if not res:
            return False
        else:
            return res[0][0]
