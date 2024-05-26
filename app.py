import tkinter as tk
from tkinter import messagebox
import requests
import cv2
from PIL import Image, ImageTk
import threading

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

def clear_widgets():
    global cap
    if cap:
        cap.release()
    for widget in root.winfo_children():
        widget.destroy()

def show_login_page():
    global cap
    cap = None  # Ensure cap is reset when returning to the login page
    clear_widgets()
    root.title("CCTV LPR")
    center_window(root, 500, 500)
    tk.Label(root, text="Username:").pack()
    global entry_user
    entry_user = tk.Entry(root)
    entry_user.pack()
    tk.Label(root, text="Password:").pack()
    global entry_pass
    entry_pass = tk.Entry(root, show="*")
    entry_pass.pack()
    tk.Button(root, text="Login", command=verify_login).pack()

def verify_login():
    username = entry_user.get()
    password = entry_pass.get()
    try:
        response = requests.post('http://127.0.0.1:5000/login', json={"username": username, "password": password}, verify=False)
        if response.status_code == 200:
            response_data = response.json()
            ip_address = response_data.get("ip_address", "N/A")
            login_success(username, ip_address)
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Login Failed", str(e))

def login_success(username, ip_address):
    clear_widgets()
    root.title("LPR")
    #tk.Label(root, text=f"Welcome {username} to LPR (License Plate Recognition) Application").pack(side='top', fill='x')
    tk.Label(root, text=f"camera1").pack(side='top', fill='x')

    video_url = f"{ip_address}"  # Adjusted for RTSP stream
    global cap
    cap = cv2.VideoCapture(video_url)

    def update_frame():
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv_frame)
                imgtk = ImageTk.PhotoImage(image=img.resize((500, 500)))
                video_label.imgtk = imgtk
                video_label.configure(image=imgtk)
            video_label.after(100, update_frame)  # Adjusted refresh rate to 100 ms
        else:
            video_label.after(100, update_frame)  # Keep trying if cap isn't opened yet

    video_label = tk.Label(root)
    video_label.pack()
    update_frame()

    logout_button = tk.Button(root, text="Logout", command=show_login_page)
    logout_button.pack(side='right', padx=5, pady=5)

    center_window(root, 800, 600)

root = tk.Tk()
show_login_page()
root.mainloop()
