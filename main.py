import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import subprocess
import os
import time
import webbrowser
from plyer import notification
from PIL import Image, ImageTk
import cv2
import platform
import random
import string
from pushbullet import Pushbullet

LOG_FILE = "log.txt"
PASSWORD = "st7584"

def send_push_notification(message):
    api_key = "o.5MxdOMWcXpcPJQ7dAfR8X72wbDRoYlfj"
    pb = Pushbullet(api_key)
    pb.push_note("⚠ WebCam Security Alert", message)

# Example usage
send_push_notification("Intruder detected! Check your webcam logs.")

# Function to generate random password
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Function to change password
def change_password():
    global PASSWORD
    choice = messagebox.askyesno("Generate Random Password", "Would you like to generate a random password?")
    if choice:
        new_password = generate_random_password()
        PASSWORD = new_password
        messagebox.showinfo("Random Password Generated", f"New password: {new_password}")
    else:
        new_password = simpledialog.askstring("Change Password", "Enter new password:")
        if new_password:
            PASSWORD = new_password
            messagebox.showinfo("Change Password", "Password successfully changed.")

# Function to check camera status
def check_status():
    try:
        system_os = platform.system()
        
        if system_os == "Windows":
            command = r'REG QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam" /v Value'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if "0x0" in result.stdout:
                status = "Camera is DISABLED"
            else:
                status = "Camera is ENABLED"

        elif system_os == "Linux":
            result = subprocess.run("ls /dev/video*", shell=True, capture_output=True, text=True)
            status = "Camera is ENABLED" if "/dev/video" in result.stdout else "Camera is DISABLED"

        elif system_os == "Darwin":  # macOS
            result = subprocess.run("ioreg -r -c AppleCameraInterface", shell=True, capture_output=True, text=True)
            status = "Camera is ENABLED" if "AppleCameraInterface" in result.stdout else "Camera is DISABLED"

        else:
            status = f"Unsupported OS: {system_os}"

        messagebox.showinfo("Check Status", status)

    except Exception as e:
        messagebox.showerror("Error", f"Could not check status: {e}")

# Function to view logs
def view_logs():
    log_window = tk.Toplevel(root)
    log_window.title("View Logs")
    log_window.geometry("500x400")

    text_area = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=("Arial", 12))
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as log_file:
            logs = log_file.read()
        text_area.insert(tk.END, logs)
    else:
        text_area.insert(tk.END, "No logs available.")

    def clear_logs():
        open(LOG_FILE, "w").close()
        text_area.delete(1.0, tk.END)
        messagebox.showinfo("Clear Logs", "Logs have been cleared.")

    clear_button = tk.Button(log_window, text="Clear Logs", bg="red", fg="white", font=("Arial", 12), command=clear_logs)
    clear_button.pack(pady=10)

# Function to show project info page (replace with your actual file path if needed)
def project_info():
    try:
        file_path = os.path.join(os.getcwd(), "project_info.html")  # or hardcode your actual file path
        webbrowser.open(f"file:///C:/Users/pathi/Documents/ST%23IS%237584-SUPRAJAproj/project_info.html")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open project info: {e}")

# Function to log events with timestamp
def log_event(event):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{timestamp}] {event}\n")
    notification.notify(
        title="WebCam Security",
        message=event,
        timeout=5
    )

# Function to capture and save snapshot
def capture_snapshot():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        filename = f"intruder_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        log_event(f"Intruder snapshot saved as {filename}")
    cap.release()
    cv2.destroyAllWindows()

# Other functions (view_logs, check_status, disable_camera, enable_camera, etc.) remain unchanged
# I will shorten here, but assume your original functions like view_logs(), check_status() etc. are present

# Function to record short video (optional, can keep or remove if only snapshots are needed)
def record_video():
    video_filename = f"intruder_{int(time.time())}.avi"
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
    start_time = time.time()
    while int(time.time() - start_time) < 5:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    log_event(f"Intruder video saved as {video_filename}")

# Password protected camera control
def camera_control(action):
    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x200")
    tk.Label(password_window, text="Enter Password:").pack()
    password_entry = tk.Entry(password_window, show="*")
    password_entry.pack()
    error_label = tk.Label(password_window, text="", font=("Arial", 12), fg="red")
    error_label.pack()

    def verify_password():
        if password_entry.get() == PASSWORD:
            if action == "disable":
                disable_camera() # type: ignore
            elif action == "enable":
                enable_camera() # type: ignore
            password_window.destroy()
        else:
            error_label.config(text="Incorrect password. Please try again.")
            password_entry.delete(0, tk.END)
            capture_snapshot()  # 📸 Save snapshot on wrong attempt
            # record_video()  # Optional: you can uncomment to also record video

    tk.Button(password_window, text="OK", command=verify_password).pack()

# Main GUI (same as your original)
root = tk.Tk()
root.title("Web Cam Security")
root.geometry("400x550")
root.configure(bg="black")

tk.Label(root, text="WebCam Spyware Security", font=("Arial", 18, "bold"), fg="white", bg="black").pack(pady=10)

image_path = "pic.jpg"
try:
    img = Image.open(image_path)
    img = img.resize((150, 150), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    tk.Label(root, image=img, bg="black").pack(pady=10)
except Exception as e:
    print(f"Error loading image: {e}")

tk.Button(root, text="Project Info", bg="red", fg="white", font=("Arial", 12), command=project_info).pack(pady=5)

button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=20)

tk.Button(button_frame, text="View Logs", bg="red", fg="white", font=("Arial", 12), command=view_logs).grid(row=0, column=0, padx=10, pady=5)
tk.Button(button_frame, text="Check Status", bg="red", fg="white", font=("Arial", 12), command=check_status).grid(row=0, column=1, padx=10, pady=5)
tk.Button(button_frame, text="Change Password", bg="red", fg="white", font=("Arial", 12), command=change_password).grid(row=1, column=0, columnspan=2, pady=5)

control_frame = tk.Frame(root, bg="gray")
control_frame.pack(pady=20, fill=tk.X, padx=30)

tk.Button(control_frame, text="Disable Camera", bg="red", fg="white", font=("Arial", 12),
          command=lambda: camera_control("disable")).pack(pady=10, padx=20, fill=tk.X)
tk.Button(control_frame, text="Enable Camera", bg="red", fg="white", font=("Arial", 12),
          command=lambda: camera_control("enable")).pack(pady=10, padx=20, fill=tk.X)

root.mainloop()