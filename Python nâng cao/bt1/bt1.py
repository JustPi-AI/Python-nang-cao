import tkinter as tk
from tkinter import ttk

win = tk.Tk()
# Thiết lập tiêu đề cửa sổ
win.title("Mạc Duy Phúc")

# Create a style object
style = ttk.Style()

# Configure the LabelFrame title text color to blue
style.configure("TLabelframe.Label", foreground="blue")

mighty = ttk.LabelFrame(win, text=' Nhap ',style='TLabelframe')  
mighty.grid(column=0, row=0, padx=8, pady=4)

mighty2 = ttk.LabelFrame(win, text=' Tinh Toan ', style='TLabelframe')
mighty2.grid(column=1, row=0, padx=8, pady=4)

mighty3 = ttk.LabelFrame(win, text=' Ket Qua ', style='TLabelframe')
mighty3.grid(column=0, row=1, padx=8, pady=4, columnspan=2)

#----Nhap----
num1_label = ttk.Label(mighty, text="Enter a number 1:")
num1_label.grid(column=0, row=0, sticky='W')

num2_label = ttk.Label(mighty, text="Enter a number 2:")
num2_label.grid(column=0, row=1, sticky='W')

# Ô nhập số đầu tiên
number = tk.StringVar()
number_entered = ttk.Entry(mighty, width=12, textvariable=number)
number_entered.grid(column=1, row=0)

# Ô nhập số thứ hai
number1 = tk.StringVar()
number_entered1 = ttk.Entry(mighty, width=12, textvariable=number1)
number_entered1.grid(column=1, row=1)

def click_me():
    try:
        num1 = float(number.get())
        num2 = float(number1.get())
        operation = operator.get()

        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            if num2 != 0:
                result = num1 / num2
            else:
                result = "Không thể chia cho 0"
        else:
            result = "Phép tính không hợp lệ"

        ketqua_entry.config(state='normal')  # Cho phép chỉnh sửa để nhập kết quả
        ketqua_entry.delete(0, tk.END)       # Xóa dữ liệu cũ
        ketqua_entry.insert(0, str(result))  # Hiển thị kết quả
        ketqua_entry.config(state='readonly') # Đặt lại thành chỉ đọc
    except ValueError:
        ketqua_entry.config(state='normal')
        ketqua_entry.delete(0, tk.END)
        ketqua_entry.insert(0, "Lỗi nhập liệu")
        ketqua_entry.config(state='readonly')

#----Tinh Toan----
# Nút "Click Me"
action = tk.Button(mighty2, text="Click Me", command=click_me)
action.grid(column=1, row=0)

# Ô chọn phép tính
operator = tk.StringVar()
operator_combobox = ttk.Combobox(mighty2, width=10, textvariable=operator)
operator_combobox['values'] = ('+', '-', '*', '/')
operator_combobox.grid(column=0, row=0)
operator_combobox.current(0)

#----Ket Qua----
# Ô hiển thị kết quả
ketqua_label = tk.Label(mighty3, text="Kết quả:")
ketqua_label.grid(column=0, row=3)

ketqua_entry = ttk.Entry(mighty3, width=47, state='readonly')
ketqua_entry.grid(column=1, row=3, columnspan=2)

# Start the main event loop
win.mainloop()

