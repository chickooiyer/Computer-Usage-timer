import sys
import ctypes  # For Windows lock
import os
import platform
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTimeEdit,
    QPushButton, QMessageBox, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound

class TimeLockerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        self.create_tray_icon()

    def init_ui(self):
        self.setWindowTitle("Computer Usage Timer")
        self.resize(300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Set the time limit (HH:MM:SS):")
        layout.addWidget(self.label)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setTime(QTime(0, 30, 0))  # Default: 30 minutes
        layout.addWidget(self.time_edit)

        self.start_button = QPushButton("Start Timer")
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Timer")
        self.stop_button.clicked.connect(self.stop_timer)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.countdown_label = QLabel("Time remaining: 00:00:00")
        layout.addWidget(self.countdown_label)

        self.setLayout(layout)

    def start_timer(self):
        if self.timer.isActive():
            return  # Prevent multiple starts

        selected_time = self.time_edit.time()
        self.remaining_time = selected_time.hour() * 3600 + selected_time.minute() * 60 + selected_time.second()

        if self.remaining_time > 0:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.timer.start(1000)
            self.update_timer()
        else:
            QMessageBox.warning(self, "Invalid Time", "Please set a valid time greater than zero.")

    def stop_timer(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.countdown_label.setText("Timer Stopped")

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            hours = self.remaining_time // 3600
            minutes = (self.remaining_time % 3600) // 60
            seconds = self.remaining_time % 60
            self.countdown_label.setText(f"Time remaining: {hours:02}:{minutes:02}:{seconds:02}")

            if self.remaining_time == 10:  # 10 sec warning
                QSound.play("alert.wav")  # Ensure alert.wav exists
        else:
            self.timer.stop()
            self.lock_computer()

    def lock_computer(self):
        QMessageBox.information(self, "Time's Up", "Your usage time is over. Locking now.")
        if platform.system() == "Windows":
            ctypes.windll.user32.LockWorkStation()
        elif platform.system() == "Linux":
            os.system("gnome-screensaver-command -l" if "gnome" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower() else "qdbus org.freedesktop.ScreenSaver /ScreenSaver Lock")
        elif platform.system() == "Darwin":  # macOS
            os.system("osascript -e 'tell application \"System Events\" to sleep'")
        else:
            QMessageBox.warning(self, "Unsupported OS", "Locking is not supported on this OS.")

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        menu = QMenu()

        restore_action = QAction("Open", self)
        restore_action.triggered.connect(self.show)
        menu.addAction(restore_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.show)
        self.tray_icon.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TimeLockerApp()
    main_window.show()
    sys.exit(app.exec_())
