import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTimeEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer, QTime
import ctypes  # Used for locking the screen on Windows systems
import os
import platform

class TimeLockerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0

    def init_ui(self):
        self.setWindowTitle("Computer Usage Timer")
        self.resize(300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Set the time limit (HH:MM:SS):")
        layout.addWidget(self.label)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setTime(QTime(0, 30, 0))  # Default time: 30 minutes for usage
        layout.addWidget(self.time_edit)

        self.start_button = QPushButton("Start Timer")
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        self.countdown_label = QLabel("Time remaining: 00:00:00")
        layout.addWidget(self.countdown_label)

        self.setLayout(layout)

    def start_timer(self):
        selected_time = self.time_edit.time()
        self.remaining_time = selected_time.hour() * 3600 + selected_time.minute() * 60 + selected_time.second()

        if self.remaining_time > 0:
            self.timer.start(1000)  # Trigger every 1 second (1000 milliseconds)
            self.update_timer()
        else:
            QMessageBox.warning(self, "Invalid Time", "Please set a valid time greater than zero.")

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1

            hours = self.remaining_time // 3600
            minutes = (self.remaining_time % 3600) // 60
            seconds = self.remaining_time % 60

            self.countdown_label.setText(f"Time remaining: {hours:02}:{minutes:02}:{seconds:02}")
        else:
            self.timer.stop()
            self.lock_computer()

    def lock_computer(self):
        QMessageBox.information(self, "Time's Up", "Your usage time is over. The computer will now be locked.")
        if platform.system() == "Windows":  # This block handles locking the screen on Windows systems
            ctypes.windll.user32.LockWorkStation()
        elif platform.system() == "Linux":
            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            if "gnome" in desktop_env:  # This block handles locking the screen on GNOME desktop environment
                os.system("gnome-screensaver-command -l")
            elif "kde" in desktop_env:  # This block handles locking the screen on KDE desktop environment
                os.system("qdbus org.freedesktop.ScreenSaver /ScreenSaver Lock")
            else:
                QMessageBox.warning(self, "Unsupported Desktop Environment", "Locking functionality is not supported for this desktop environment.")
        else:
            QMessageBox.warning(self, "Unsupported OS", "Locking functionality is not supported on this OS.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TimeLockerApp()
    main_window.show()
    sys.exit(app.exec_())
