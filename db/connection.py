from mysql import connector
from mysql.connector import Error


def connect():
    conn = connector.connect(host='taxidb.ctrkgxuwjgtd.eu-central-1.rds.amazonaws.com',
                             port=3311,
                             database='taxi',
                             user='root',
                             password='v131313s')
    if conn.is_connected():
        print('Connected')
        return conn


connection = connect()


def cursor_wrap(func):
    def wrapper(self):
        cursor = connection.cursor()
        try:
            return func(self, cursor=cursor)
        except Error as error:
            print(error)
        finally:
            cursor.close()
    return wrapper
