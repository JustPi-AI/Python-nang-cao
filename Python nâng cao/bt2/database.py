# database.py
import psycopg2
from tkinter import messagebox

# Hàm kết nối tới cơ sở dữ liệu PostgreSQL với username và password nhập từ người dùng
def connect_db(username, password):
    try:
        conn = psycopg2.connect(
            host="localhost",  
            database="postgres",
            user=username,
            password=password
        )
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return None

# Hàm tạo bảng nếu chưa tồn tại
def create_table(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        mssv VARCHAR(20)
    )
    """)
    conn.commit()
    cur.close()

# Hàm thêm sinh viên
def add_student(conn, name, mssv):
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, mssv) VALUES (%s, %s)", (name, mssv))
    conn.commit()
    cur.close()

# Hàm lấy danh sách sinh viên
def get_students(conn):
    cur = conn.cursor()
    cur.execute("SELECT name, mssv FROM students")
    rows = cur.fetchall()
    cur.close()
    return rows

# Hàm xóa sinh viên
def delete_student(conn, name, mssv):
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE name = %s AND mssv = %s", (name, mssv))
    conn.commit()
    cur.close()
