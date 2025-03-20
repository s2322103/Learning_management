from app.models.user import User
from psycopg2.extras import DictCursor # type: ignore

class ScheduleModel:
    # 生徒のリクエストを作成する
    @staticmethod
    def create_student_request(student_id, date, time_slot_id, subject):
        conn = User.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO student_requests (student_id, date, time_slot_id, subject, status)
                    VALUES (%s, %s, %s, %s, 'requested')
                """, (student_id, date, time_slot_id, subject))
                conn.commit()
                return {"message": "生徒のリクエストが正常に作成されました。"}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # 講師のリクエストを作成する
    @staticmethod
    def create_teacher_request(teacher_id, date, time_slot_id, subject):
        conn = User.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO teacher_schedules (teacher_id, date, time_slot_id, subject, status)
                    VALUES (%s, %s, %s, %s, 'available')
                """, (teacher_id, date, time_slot_id, subject))
                conn.commit()
                return {"message": "講師のスケジュールが正常に作成されました。"}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # 生徒のリクエストを取得する
    @staticmethod
    def get_all_student_requests():
        conn = User.get_db_connection()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT sr.id, s.username AS student_name, ts.time_range, sr.date, sr.subject, sr.status, sr.created_at
                    FROM student_requests sr
                    JOIN students s ON sr.student_id = s.id
                    JOIN time_slots ts ON sr.time_slot_id = ts.id
                    ORDER BY sr.date DESC, ts.time_range
                """)
                requests = cur.fetchall()
                return [dict(request) for request in requests]
        except Exception as e:
            raise e
        finally:
            conn.close()

    # 講師のリクエストを取得する
    @staticmethod
    def get_all_teacher_requests():
        conn = User.get_db_connection()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT ts.id, t.username AS teacher_name, tsl.time_range, ts.date, ts.subject, ts.status, ts.created_at
                    FROM teacher_schedules ts
                    JOIN teachers t ON ts.teacher_id = t.id
                    JOIN time_slots tsl ON ts.time_slot_id = tsl.id
                    ORDER BY ts.date DESC, tsl.time_range
                """)
                requests = cur.fetchall()
                return [dict(request) for request in requests]
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    # 管理者がスケジュールを作成する
    @staticmethod
    def create_confirmed_schedule(teacher_id, student_id, date, time_slot_id, subject):
        conn = User.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO confirmed_schedules (teacher_id, student_id, date, time_slot_id, subject, status)
                    VALUES (%s, %s, %s, %s, %s, 'scheduled')
                """, (teacher_id, student_id, date, time_slot_id, subject))

                cur.execute("""
                    UPDATE teacher_schedules
                    SET status = 'confirmed'
                    WHERE teacher_id = %s AND date = %s AND time_slot_id = %s
                """, (teacher_id, date, time_slot_id))

                cur.execute("""
                    UPDATE student_requests
                    SET status = 'confirmed'
                    WHERE student_id = %s AND date = %s AND time_slot_id = %s
                """, (student_id, date, time_slot_id))

                conn.commit()
                return {"message": "スケジュールが正常に確定されました。"}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # スケジュールを取得する
    @staticmethod
    def get_confirmed_schedules(user_id, role):
        conn = User.get_db_connection()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                if role == 'teacher':
                    cur.execute("""
                        SELECT ts.time_range, cs.date, cs.subject, cs.status, s.username AS student_name
                        FROM confirmed_schedules cs
                        JOIN time_slots ts ON cs.time_slot_id = ts.id
                        JOIN students s ON cs.student_id = s.id
                        WHERE cs.teacher_id = %s
                        ORDER BY cs.date, ts.time_range
                    """, (user_id,))
                elif role == 'student':
                    cur.execute("""
                        SELECT ts.time_range, cs.date, cs.subject, cs.status, t.username AS teacher_name
                        FROM confirmed_schedules cs
                        JOIN time_slots ts ON cs.time_slot_id = ts.id
                        JOIN teachers t ON cs.teacher_id = t.id
                        WHERE cs.student_id = %s
                        ORDER BY cs.date, ts.time_range
                    """, (user_id,))
                elif role == 'admin':
                    cur.execute("""
                        SELECT cs.id AS confirmed_schedule_id, ts.time_range, cs.date, cs.subject, cs.status,
                            s.username AS student_name, t.username AS teacher_name
                        FROM confirmed_schedules cs
                        JOIN time_slots ts ON cs.time_slot_id = ts.id
                        JOIN students s ON cs.student_id = s.id
                        JOIN teachers t ON cs.teacher_id = t.id
                        ORDER BY cs.date, ts.time_range
                    """)
                else:
                    return []

                schedules = cur.fetchall()
                return [dict(schedule) for schedule in schedules]
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_confirmed_schedule(confirmed_schedule_id, teacher_id, student_id, date, time_slot_id, subject):
        conn = User.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE confirmed_schedules
                    SET teacher_id = %s, student_id = %s, date = %s, time_slot_id = %s, subject = %s
                    WHERE id = %s
                """, (teacher_id, student_id, date, time_slot_id, subject, confirmed_schedule_id))
                conn.commit()
                return {"message": "確認済みスケジュールが正常に更新されました"}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # @staticmethod
    # def delete_confirmed_schedule(schedule_id):
    #     conn = User.get_db_connection()
    #     try:
    #         with conn.cursor() as cur:
    #             cur.execute("""
    #                 DELETE FROM confirmed_schedules
    #                 WHERE id = %s
    #             """, (schedule_id,))
    #             conn.commit()
    #             return {"message": "Confirmed schedule deleted successfully"}
    #     except Exception as e:
    #         conn.rollback()
    #         raise e
    #     finally:
    #         conn.close()

    @staticmethod
    def get_all_teachers():
        conn = User.get_db_connection()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT id,username 
                    FROM teachers 
                    ORDER BY username
                """)
                teachers = cur.fetchall()
                return [dict(teacher) for teacher in teachers]
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all_students():
        conn = User.get_db_connection()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT id, username 
                    FROM students 
                    ORDER BY username
                """)
                students = cur.fetchall()
                return [dict(student) for student in students]
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all_time_slots():
        conn = User.get_db_connection()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT id, time_range 
                    FROM time_slots 
                    ORDER BY time_range
                """)
                time_slots = cur.fetchall()
                return [dict(time_slot) for time_slot in time_slots]
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_available_subjects(user_id, role):
        if not user_id or not role:
            raise ValueError("User ID and role are required")

        conn = User.get_db_connection()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                if role == 'student':
                    cur.execute("""
                        SELECT DISTINCT unnest(subjects) as name
                        FROM students
                        WHERE id = %s
                        ORDER BY name
                    """, (user_id,))
                
                elif role == 'teacher':
                    cur.execute("""
                        SELECT DISTINCT unnest(subjects) as name
                        FROM teachers
                        WHERE id = %s
                        ORDER BY name
                    """, (user_id,))
                
                else:
                    raise ValueError("Invalid role specified")

                results = cur.fetchall()
                return [dict(row) for row in results]
        
        except Exception as e:
            raise e
        finally:
            conn.close()