from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys

from utilities import *

class btn_withIcon(QWidget):
    def __init__(self, label, context:UIContext, path, time_marker=False, empty_marker=False):
        super().__init__()
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(0)

        '''
        Send dimensions for sizing to customize between varying stretches of the layouts
        Consider turning multiline styling to fstring setStyleSheet
        If Control for adding label above buttons
        '''

        self.icon_label = imageSetter(self, path, xdim=50, ydim=50)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(f"""
                                        background-color: #decfad; 
                                        border-top-left-radius: 20px; 
                                        border-bottom-left-radius: 20px;
                                      """)
        
        self.button_label = QLabel(label)
        self.button_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_label.setStyleSheet(f"""
                                        QLabel {{
                                            background-color: #decfad;
                                            border-left: 1px solid #555;
                                            border-top-right-radius: 20px; 
                                            border-bottom-right-radius: 20px;
                                            font-weight: 800;
                                            font-size: 20px;
                                            color: #6D94C5;
                                        }}
                                        QLabel:hover {{
                                            background-color: #b39f72;
                                            color: black;
                                        }}
                                        """)

        self.button_layout.addWidget(self.icon_label, stretch=2)
        self.button_layout.addWidget(self.button_label, stretch=5)

        if time_marker:
            self.withTimeLayout = QVBoxLayout()
            self.popup = nextAppearHelp()
            if empty_marker: self.time_label = QLabel('')
            else: 
                self.time_label = interactableLabel('Next Appearance: ', self.popup)
                self.time_label.setStyleSheet("""
                QWidget {
                    border-radius: 10px;
                    background-color: #b39f72;
                    font-family: Open Sans;
                    font-size: 18px; 
                    font-weight: 500; 
                    color: white;
                }
                QLabel::hover {
                    background-color: #b3a68b;
                    border-radius: 10px;
                    color: black;
                }
            """)
            self.withTimeLayout.addWidget(self.time_label, stretch=1)
            self.withTimeLayout.addLayout(self.button_layout, stretch=3)
            self.setLayout(self.withTimeLayout)
        else:
            self.setLayout(self.button_layout)

        context.setShadow(self, 8, 8, 15, 200)
        self.mousePressEvent = lambda event: self.pseudoPressEvent(event)

    def styleButtons(self, widget):
        if widget == self.icon_label:
            widget.setStyleSheet()

    def pseudoPressEvent(self, event):
        print('Pressed\n')

class cardReviewWindow(QWidget):
    def __init__(self, context:UIContext=None):
        super().__init__()
        self.context = context
        self.setStyleSheet('background-color: #05061b;')
        self.setFixedSize(1350, 695)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.setLayout(self.main_layout)

        resource_path = self.context.prog_path / "Resources"
        galaxy_decor = imageSetter(self, str(resource_path / "Galaxy.jpg"), 1075, -15, 300, 300, decor=True)
        self.context.widgetOpacitySetter(galaxy_decor, 0.7)

        stars_decor = imageSetter(self, str(resource_path / "stars3.png"), 0, 0, 1350, 695, decor=True)
        self.context.widgetOpacitySetter(stars_decor, 0.7)

        saturn_decor = imageSetter(self, str(resource_path / "Saturn.jpg"), 950, 300, 500, 464, decor=True)
        self.context.widgetOpacitySetter(saturn_decor, 0.6)

        # book_decor = imageSetter(self, str(resource_path / "book.png"), 380, -125, 600, 600, decor=True)
        # self.context.widgetOpacitySetter(book_decor, 0.80)

        scroll_decor = imageSetter(self, str(resource_path / "scroll.png"), -30, 130, 300, 156, decor=True)
        self.context.widgetOpacitySetter(scroll_decor, 0.25)

        flask_decor = imageSetter(self, str(resource_path / "flask.png"), 110, 275, 130, 130, decor=True)
        self.context.widgetOpacitySetter(flask_decor, 0.25)

        pi_decor = imageSetter(self, str(resource_path / "pi.png"), -60, 550, 250, 130, decor=True)
        self.context.widgetOpacitySetter(pi_decor, 0.25)

        paint_decor = imageSetter(self, str(resource_path / "Paint.png"), 1200, 300, 130, 120, decor=True)

        self.homeButton()
        self.reviewActions()

        stars_decor.raise_()
        
        self.main_layout.addWidget(self.button_container, stretch=1)
       
        # book_decor.raise_()
        scroll_decor.raise_()
        flask_decor.raise_()
        pi_decor.raise_()
        paint_decor.raise_()
        galaxy_decor.raise_()
        saturn_decor.raise_()
        
        self.main_layout.addLayout(self.cardPaneLayout, stretch=6)      

    def homeButton(self):
        self.button_container = QWidget()
        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(80, 10, 10, 20)
        widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align the entire layout left
        self.button_container.setLayout(widget_layout)

        resource_path = self.context.prog_path / "Resources"
        button1 = btn_withIcon('Home', self.context, str(resource_path / "home-icon.png"))
        button1.setMaximumWidth(300)
        widget_layout.addWidget(button1)

    def reviewActions(self):
        self.cardPaneLayout = QVBoxLayout()
        self.cardPaneLayout.setSpacing(3)
        self.cardPaneLayout.setContentsMargins(200, 0, 200, 0)

        self.cardDisplay = QLabel()
        self.context.setShadow(self.cardDisplay, 12, 12, 8, 200)
        self.cardDisplay.setStyleSheet('background-color: #253463; border-radius: 30px;')

        button_layout = QHBoxLayout()
        resource_path = self.context.prog_path / "Resources"
        button1 = btn_withIcon('Flip', self.context, str(resource_path / "flip.png"), time_marker=True, empty_marker=True)
        button2 = btn_withIcon('Again', self.context, str(resource_path / "again.png"), time_marker=True)
        button3 = btn_withIcon('Next', self.context, str(resource_path / "next.png"), time_marker=True)

        button_layout.addWidget(button1)
        button_layout.addWidget(button2)
        button_layout.addWidget(button3)

        self.cardPaneLayout.addWidget(self.cardDisplay, stretch=4)
        self.cardPaneLayout.addLayout(button_layout, stretch=1)

class nextAppearHelp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Next Apperance')
        self.setStyleSheet('background-color: #141c36;')
        
        self.setWindowFlags(
            Qt.WindowType.Tool | #Make it a tool window instead of QWidget
            Qt.WindowType.WindowStaysOnTopHint #Make the window stay on top
        )
        self.resize(300, 150)
        header = QLabel('Subtopic Folder Instructions')
        header.setStyleSheet('font-size: 25px; color: #fae2be;')
        description = QLabel("""Guide:
            ⚫To Begin Review
                             🟢 Select a Subject and Double Click on a Topic
                             🟢 Or Select a Topic and Click Review Button
            ⚫To Create New Topic
                             1) Press Add Folder
                             2) Select a Subject Folder from Main Menu
                             3) Enter Name of New Subtopic
                             4) Select Folder Type: New Subtopic
                             5) Press Create
                            """)
        description.setStyleSheet('color: #fae2be')

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(description)

        self.setLayout(layout)

class imageSetter(QLabel):
    def __init__(self, parent, path, xpos=None, ypos=None, xdim=None, ydim=None, decor=False):
        super().__init__(parent=parent) #Allow the label to show through the parent
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)
        self.setScaledContents(True)

        if xdim and ydim:
            self.setFixedSize(xdim, ydim)
        if decor: 
            self.move(xpos, ypos)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    reviewScreen = cardReviewWindow()
    reviewScreen.show()
    app.exec()
