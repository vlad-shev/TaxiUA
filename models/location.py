from db.connection import connection, cursor_wrap


class Location:
    def __init__(self, region, city):
        self.region = region
        self.city = city

    @cursor_wrap
    def save(self, cursor):
        if not self.get_id():
            cursor.execute(f"INSERT INTO location VALUES(NULL,'{self.region}','{self.city}')")
            print('Location added')
            connection.commit()
        else:
            print('Location already exist')

    @cursor_wrap
    def get_id(self, cursor):
        cursor.execute(f"SELECT id FROM location WHERE region='{self.region}' and city='{self.city}'")
        res = cursor.fetchall()
        if not res:
            return False
        else:
            return res[0][0]
