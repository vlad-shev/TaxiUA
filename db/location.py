from db.connection import cursor_wrap


@cursor_wrap
def get_regions(self, cursor):
    cursor.execute('SELECT DISTINCT region FROM location')
    res = cursor.fetchall()
    return res


@cursor_wrap
def get_cities(user, cursor):
    cursor.execute(f"SELECT DISTINCT city FROM location WHERE region='{user.region}'")
    res = cursor.fetchall()
    return res
