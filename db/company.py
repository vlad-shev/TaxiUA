from db.connection import cursor_wrap


@cursor_wrap
def get_companies(user, cursor):
    cursor.execute(f"SELECT name FROM company WHERE location={user.location}")
    res = cursor.fetchall()
    return res


@cursor_wrap
def get_company_info(user, cursor):
    cursor.execute("SELECT id, description, phone FROM company WHERE location='{}' AND name='{}'".format(
        user.location, user.last_company))
    res = cursor.fetchall()[0]
    return res
