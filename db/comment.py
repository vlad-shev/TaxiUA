from db.connection import cursor_wrap, connection
from models.user import User

@cursor_wrap
def save_comment(user, cursor):
    cursor.execute(f"INSERT INTO comment(user_id, company_id, text) VALUES({user.id},{user.last_company_id},'{user.msg.text}')")
    print('Comment added')
    connection.commit()


@cursor_wrap
def get_comments(user, cursor):
    cursor.execute('{} {}'.format("SELECT comment.user_id, comment.date, comment.text FROM comment",
                                 f"WHERE comment.company_id={user.last_company_id} ORDER BY date DESC"))
    res = cursor.fetchall()
    return res
