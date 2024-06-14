import sys
import threading
import queue
import requests
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

class VideoStreamHandler:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.cap = cv2.VideoCapture(self.ip_address)
        self.frame_queue = queue.Queue(maxsize=10)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.capture_frames)
        self.thread.start()

    def capture_frames(self):
        while not self.stop_event.is_set():
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    try:
                        frame = cv2.resize(frame, (640, 480))
                        if not self.frame_queue.full():
                            self.frame_queue.put(frame)
                        else:
                            print("Dropping frame to catch up...")
                    except cv2.error as e:
                        print(f"Error processing frame: {e}")
                else:
                    print("Failed to read frame, reconnecting...")
                    self.reconnect_stream()
            else:
                print("Reconnecting...")
                self.reconnect_stream()

    def get_frame(self):
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def reconnect_stream(self):
        self.cap.release()
        self.cap = cv2.VideoCapture(self.ip_address)

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        if self.cap:
            self.cap.release()


class VideoWindow(QWidget):
    def __init__(self, ip_address):
        super().__init__()
        self.stream_handler = VideoStreamHandler(ip_address)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Stream')
        self.setGeometry(500, 500, 800, 600)

        self.image_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        self.logout_button = QPushButton('Logout', self)
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        frame = self.stream_handler.get_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.stream_handler.stop()

    def logout(self):
        self.stream_handler.stop()
        self.close()  # Assuming there's a method to handle re-showing login or cleanup

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login with Server Check')
        self.setGeometry(300, 300, 200, 150)

        layout = QVBoxLayout()

        self.username_label = QLabel('Username:', self)
        layout.addWidget(self.username_label)
        self.username_entry = QLineEdit(self)
        layout.addWidget(self.username_entry)

        self.password_label = QLabel('Password:', self)
        layout.addWidget(self.password_label)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        login_button = QPushButton('Login', self)
        login_button.clicked.connect(self.verify_login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def verify_login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        try:
            response = requests.post('http://127.0.0.1:5001/login', json={"username": username, "password": password}, verify=False)
            if response.status_code == 200:
                response_data = response.json()
                ip_address = response_data.get("ip_address", "N/A")
                self.open_video_window(ip_address)
            else:
                QMessageBox.critical(self, 'Login Failed', 'Invalid Username or Password')
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Login Failed', str(e))

    def open_video_window(self, ip_address):
        self.video_window = VideoWindow(ip_address)
        self.video_window.show()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginWindow()
    ex.show()
    sys.exit(app.exec_())
