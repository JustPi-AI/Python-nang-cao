# ui.py
import tkinter as tk
from tkinter import messagebox
import database  # Import file database.py

# Hàm đăng nhập
def login_user():
    username = login_username_entry.get()
    password = login_password_entry.get()
    
    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return
    
    # Thử kết nối với cơ sở dữ liệu
    conn = database.connect_db(username, password)
    
    if conn:
        messagebox.showinfo("Login Success", "Logged in successfully!")
        # Mở cửa sổ quản lý sinh viên sau khi đăng nhập thành công
        open_student_management(conn)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Hàm mở cửa sổ quản lý sinh viên
def open_student_management(conn):
    # Giao diện quản lý sinh viên
    root = tk.Tk()
    root.title("Student Management")

    # Tạo bảng sinh viên nếu chưa có
    database.create_table(conn)

    # Hàm thêm sinh viên
    def add_student():
        name = name_entry.get()
        mssv = mssv_entry.get()

        if name and mssv:
            database.add_student(conn, name, mssv)
            name_entry.delete(0, tk.END)
            mssv_entry.delete(0, tk.END)
            load_students()  
        else:
            messagebox.showwarning("Input Error", "Please enter both name and MSSV.")

    # Hàm tải danh sách sinh viên
    def load_students():
        student_list.delete(0, tk.END)
        rows = database.get_students(conn)
        for row in rows:
            student_list.insert(tk.END, f"Name: {row[0]}, MSSV: {row[1]}")

    # Hàm xóa sinh viên
    def delete_student():
        selected = student_list.curselection()
        if selected:
            student_info = student_list.get(selected[0])
            name, mssv = parse_student_info(student_info)
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name} (MSSV: {mssv})?")
            if confirm:
                database.delete_student(conn, name, mssv)
                load_students()

    # Hàm tách tên và MSSV từ chuỗi
    def parse_student_info(student_info):
        parts = student_info.split(", ")
        name = parts[0].replace("Name: ", "")
        mssv = parts[1].replace("MSSV: ", "")
        return name, mssv

    # Giao diện quản lý sinh viên
    tk.Label(root, text="Name:").grid(row=0, column=0, padx=10, pady=10)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="MSSV:").grid(row=1, column=0, padx=10, pady=10)
    mssv_entry = tk.Entry(root)
    mssv_entry.grid(row=1, column=1, padx=10, pady=10)

    add_button = tk.Button(root, text="Add Student", command=add_student)
    add_button.grid(row=2, column=0, columnspan=2, pady=10)

    delete_button = tk.Button(root, text="Delete Student", command=delete_student)
    delete_button.grid(row=4, column=0, columnspan=2, pady=10)

    student_list = tk.Listbox(root, width=50)
    student_list.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    load_students()

    root.mainloop()

# Giao diện đăng nhập
login_window = tk.Tk()
login_window.title("Login")

tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
login_username_entry = tk.Entry(login_window)
login_username_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=10, pady=10)
login_password_entry = tk.Entry(login_window, show="*")
login_password_entry.grid(row=1, column=1, padx=10, pady=10)

login_button = tk.Button(login_window, text="Login", command=login_user)
login_button.grid(row=2, column=0, columnspan=2, pady=10)

login_window.mainloop()
