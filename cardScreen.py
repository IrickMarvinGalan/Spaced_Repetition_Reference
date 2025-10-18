from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import json, os, sys


class Card:
    def __init__(self, front, back):
        self.front = front
        self.back = back
        
        
class CardCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Card Creation Menu")
        self.setGeometry(400, 200, 800, 650)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#3e2f7a"))
        self.setPalette(palette)
        
        self.folder_path = None
        self.initUI()

    def initUI(self):
        create_layout = QVBoxLayout()
        create_layout.setContentsMargins(40, 30, 40, 30)
        create_layout.setSpacing(15)

        top_bar = QHBoxLayout()
        front_label = QLabel("Front")
        front_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        front_label.setFont(QFont("Arial Rounded MT Bold", 12))
        front_label.setStyleSheet("""
            QLabel {
                background-color: #e6d8b4;
                color: #2c3e50;
                border-radius: 12px;
                padding: 6px 20px;
            }
        """)
        top_bar.addWidget(front_label, alignment=Qt.AlignmentFlag.AlignLeft)

        folder_button = QPushButton("📁 Folder Name")
        folder_button.setFont(QFont("Arial", 10))
        folder_button.setStyleSheet("""
            QPushButton {
                background-color: #e6d8b4;
                color: #2c3e50;
                
                border-radius: 12px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ddcd9e; }
        """)
        top_bar.addWidget(folder_button, alignment=Qt.AlignmentFlag.AlignRight)
        create_layout.addLayout(top_bar)

        self.front_text = QTextEdit()
        self.front_text.setPlaceholderText("Insert Here")
        self.front_text.setStyleSheet("""
            QTextEdit {
                background-color: #e6d8b4;
                border-radius: 10px;
                color: #2c3e50;
                font-size: 14px;
                padding: 10px;
            }
        """)
        create_layout.addWidget(self.front_text)

        back_label = QLabel("Back")
        back_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        back_label.setFont(QFont("Arial Rounded MT Bold", 12))
        back_label.setStyleSheet("""
            QLabel {
                background-color: #e6d8b4;
                color: #2c3e50;
                border-radius: 12px;
                padding: 6px 20px;
            }
        """)
        create_layout.addWidget(back_label, alignment=Qt.AlignmentFlag.AlignLeft)

        self.back_text = QTextEdit()
        self.back_text.setPlaceholderText("Insert Here")
        self.back_text.setStyleSheet("""
            QTextEdit {
                background-color: #e6d8b4;
                border-radius: 10px;
                color: #2c3e50;
                font-size: 14px;
                padding: 10px;
            }
        """)
        create_layout.addWidget(self.back_text)

        create_btn = QPushButton("Create")
        create_btn.setFont(QFont("Arial Rounded MT Bold", 12))
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #e6d8b4;
                color: #2c3e50;
                border-radius: 12px;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #ddcd9e;
            }
        """)
        create_layout.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(create_layout)

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CardCreator()
    window.show()
    sys.exit(app.exec())