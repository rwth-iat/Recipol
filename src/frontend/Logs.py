# src/frontend/Logs.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QTextCursor
from qfluentwidgets import TextEdit, SubtitleLabel


class LogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("log_page")

        layout = QVBoxLayout(self)
        layout.addWidget(SubtitleLabel("Execution Log", self))

        self.log_edit = TextEdit(self)
        self.log_edit.setReadOnly(True)

        layout.addWidget(self.log_edit, 1)

    def append_log(self, msg: str):
        self.log_edit.append(msg)
        self.log_edit.moveCursor(QTextCursor.MoveOperation.End)
