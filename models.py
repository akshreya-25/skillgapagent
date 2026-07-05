from flask_login import UserMixin
from database import get_db_connection

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row['id'], username=row['username'], email=row['email'], password=row['password'])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row['id'], username=row['username'], email=row['email'], password=row['password'])
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row['id'], username=row['username'], email=row['email'], password=row['password'])
        return None
