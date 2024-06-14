import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QTimer 
import requests
import cv2
from PyQt5.QtGui import QImage, QPixmap
import numpy as np

# Global initialization of the cap variable
cap = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CCTV LPR')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.apply_styles()
        self.show_login_page()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
                background-color: white; /* Set the background color to white */
            }
            QLabel {
                color: #333;
                font-weight: bold; /* Make text bold */
            }
            QLineEdit {
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 4px;
                background-color: white;
                color: black;
                width: 200px; /* Smaller width */
                max-width: 200px;
            }
            QPushButton {
                background-color: #5CACEE;
                color: white;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
        """)

    def clear_widgets(self):
        global cap
        if cap is not None:
            cap.release()
            cap = None
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


    def center_window(self, width, height):
        screen = self.screen().geometry()
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def show_login_page(self):
        self.clear_widgets()
        self.setWindowTitle("CCTV LPR")
        self.center_window(500, 500)

        # Layout for username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:", self)
        username_layout.addWidget(username_label)
        self.entry_user = QLineEdit(self)
        username_layout.addWidget(self.entry_user)
        self.layout.addLayout(username_layout)

        # Layout for password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:", self)
        password_layout.addWidget(password_label)
        self.entry_pass = QLineEdit(self)
        self.entry_pass.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.entry_pass)
        self.layout.addLayout(password_layout)

        login_button = QPushButton("Login", self)
        login_button.clicked.connect(self.verify_login)
        self.layout.addWidget(login_button)

    def verify_login(self):
        username = self.entry_user.text()
        password = self.entry_pass.text()
        try:
            response = requests.post('http://127.0.0.1:5001/login', json={"username": username, "password": password}, verify=False)
            if response.status_code == 200:
                response_data = response.json()
                ip_address = response_data.get("ip_address", "N/A")
                self.login_success(username, ip_address)
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid Username or Password")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Login Failed", str(e))

    def login_success(self, username, ip_address):
        self.clear_widgets()
        self.setWindowTitle("LPR System")

        # Start video capture
        global cap
        cap = cv2.VideoCapture(ip_address)

        # Create and add the video display label to the layout
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)
        self.update_frame()

        # Create and add a logout button to the layout
        logout_button = QPushButton("Logout", self)
        logout_button.clicked.connect(self.show_login_page)
        self.layout.addWidget(logout_button)

        # Adjust the window size for the video and logout button
        self.center_window(800, 600)


    def update_frame(self):
        global cap
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qImg))
            else:
                print("Failed to capture frame")  # Add more robust logging or error handling here
        QTimer.singleShot(100, self.update_frame)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
