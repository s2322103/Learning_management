import psycopg2 # type: ignore
from werkzeug.security import generate_password_hash

class User:
    def __init__(self, id, username, password_hash=None, role=None, **kwargs):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.additional_info = kwargs

    @staticmethod
    def get_db_connection():
        return psycopg2.connect(dbname="nsota", user="nsota", password="p3qHkNhq", host="localhost")

    @classmethod
    def create_user(cls, username, password, role, **kwargs):
        """
        ユーザーを指定された役割に基づいて作成します。
        role: 'student', 'teacher', 'admin' のいずれか
        kwargs: 追加のフィールド（例: grade, subjects）
        """
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cur:
                password_hash = generate_password_hash(password)

                if role == 'student':
                    grade = kwargs.get('grade', None)
                    subjects = kwargs.get('subjects', [])
                    cur.execute(
                        """
                        INSERT INTO students (username, password, grade, subjects)
                        VALUES (%s, %s, %s, %s) RETURNING id
                        """,
                        (username, password_hash, grade, subjects)
                    )
                elif role == 'teacher':
                    subjects = kwargs.get('subjects', [])
                    cur.execute(
                        """
                        INSERT INTO teachers (username, password, subjects)
                        VALUES (%s, %s, %s) RETURNING id
                        """,
                        (username, password_hash, subjects)
                    )
                elif role == 'admin':
                    cur.execute(
                        """
                        INSERT INTO admins (username, password)
                        VALUES (%s, %s) RETURNING id
                        """,
                        (username, password_hash)
                    )
                else:
                    raise ValueError("Invalid role specified.")

                user_id = cur.fetchone()[0]
                conn.commit()
                return cls(id=user_id, username=username, role=role)
        finally:
            conn.close()

    @classmethod
    def get_by_username(cls, username, role):
        """
        指定されたユーザー名と役割でユーザーを取得します。
        role: 'student', 'teacher', 'admin' のいずれか
        """
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cur:
                if role == 'student':
                    cur.execute(
                        """
                        SELECT id, username, password, grade, subjects
                        FROM students WHERE username = %s
                        """,
                        (username,)
                    )
                elif role == 'teacher':
                    cur.execute(
                        """
                        SELECT id, username, password, subjects
                        FROM teachers WHERE username = %s
                        """,
                        (username,)
                    )
                elif role == 'admin':
                    cur.execute(
                        """
                        SELECT id, username, password
                        FROM admins WHERE username = %s
                        """,
                        (username,)
                    )
                else:
                    raise ValueError("Invalid role specified.")

                user = cur.fetchone()
                if user:
                    if role == 'student':
                        return cls(
                            id=user[0],
                            username=user[1],
                            password_hash=user[2],
                            role=role,
                            grade=user[3],
                            subjects=user[4]
                        )
                    elif role == 'teacher':
                        return cls(
                            id=user[0],
                            username=user[1],
                            password_hash=user[2],
                            role=role,
                            subjects=user[3]
                        )
                    elif role == 'admin':
                        return cls(
                            id=user[0],
                            username=user[1],
                            password_hash=user[2],
                            role=role
                        )
                return None
        finally:
            conn.close()

