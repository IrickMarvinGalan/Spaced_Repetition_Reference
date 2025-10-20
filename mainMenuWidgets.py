from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from pathlib import Path
from utilities import *
import os

from cardScreen import *
from reviewScreen import *

class scrollArea(QScrollArea):
    def __init__(self, context, primary_layout, strch=None, 
                 scroll_layout=None, area_type='Subfolder'):
        super().__init__()
        self.context = context
        self.area_type = area_type
        self.setWidgetResizable(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("""
            QScrollArea {
                border-left: 2px solid #555;
                background-color: #EBE1D1;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #888;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555;
            }
        """)

        # --- Create and configure scrollable area ---
        self.createFolders(primary_layout, strch, scroll_layout) #Create Folders in startup mode

        self.scrollable_widget = QWidget()
        self.scrollable_widget.setLayout(scroll_layout)

        self.setWidget(self.scrollable_widget)

    def createFolders(self, primary_layout=None, strch=None, scroll_layout=None, delete=False):
        if delete: #Delete all folder widgets before recreating the scroll area
            scroll_layout = self.context.emptyScrollArea(self)

        abs_path = Path.home()
        prog_dir = abs_path / "Documents" / "SpacedRep"

        if self.area_type == 'Subject':
            for directory in prog_dir.iterdir():
                if directory.is_dir() and directory.name != "Resources":
                    folder = self.folderWidget(self.context, directory.name, self.area_type)
                    scroll_layout.addWidget(folder)

            if isinstance(primary_layout, QLayout):
                if not primary_layout.itemAt(0): #Add a QScrollArea when the parent layout do not have any setwidget yet
                    primary_layout.addWidget(self, stretch=strch)
        
        elif self.area_type == 'Subfolder':
            if primary_layout: #Creation of main subject folder do not require subfolder widgets yet to show
                return

            if not self.context.subj_path:
                print("No subject selected yet; skipping Subfolder population")
                return
            
            #Executes when subfolders area is refreshed through new subject selection, addition, or deletion
            for directory in self.context.subj_path.iterdir(): 
                if directory.is_dir():
                    folder = self.folderWidget(self.context, directory.name, self.area_type)
                    scroll_layout.addWidget(folder)

    def refreshSubfolders(self, context, directory, widget_layout, area_type):
        folder = self.folderWidget(context, directory, area_type)
        widget_layout.addWidget(folder)
        '''Refresh the Subfolder Pointer when a new subject is selected, as previous widgets are already deleted
        And might cause an runtime error if not handled properly'''
        self.currentSubtFolderSelection = None
        self.prevSubtFolderSelection = None

    class folderWidget(QWidget):
        def __init__(self, context, directory_name, area_type='Subfolder'):
            super().__init__()
            self.context = context
            self.area_type = area_type
            self.setMaximumWidth(400)
            self.setFixedHeight(120)
            self.context.styleFolders(self, self.area_type) #Check utilities for additional info

            self.context.setShadow(self, 3, 3, 1, 80)

            label_layout = QHBoxLayout()
            self.label = QLabel(directory_name)
            self.label.setWordWrap(True)  # prevents long names from clipping text
            self.label.setMaximumWidth(400)
            self.label.setFixedHeight(120)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setStyleSheet('font-weight: 750; font-size: 22px; color: #ffffff')
            label_layout.addWidget(self.label)
            label_layout.setContentsMargins(0, 0, 0, 0) 
            
            self.setLayout(label_layout)
            self.name = self.label.text()

            self.mousePressEvent = lambda event: self.folder_clicked(event, directory_name, area_type)

            if self.area_type == 'Subfolder': #Assign a double click event for starting a review session
                self.mouseDoubleClickEvent = lambda event: self.startReview(event) 
                '''Modify Later for additional filters sent'''

        def folder_clicked(self, event, directory_name, area_type):
            if event.button() == Qt.MouseButton.LeftButton:
                self.context.selection_label.setText(f'Selected Folder: {self.name}')
                self.context.folderSelectionValidator(self.area_type)

                if area_type == 'Subject':
                    subj_dir = self.context.prog_path / directory_name
                    self.context.subj_path = subj_dir
                    self.context.isSubjectSelection = True #Toggle selection state for other functions that will use it
                    print(str(self.context.subj_path))

                    if subj_dir.exists():
                        dir_list = [d.name for d in subj_dir.iterdir() if d.is_dir()]

                        subf_scroll = self.context.scrollable_subfolders
                        if subf_scroll.widget():
                            widget_layout = self.context.emptyScrollArea(subf_scroll) #Empty the scroll area of subfolders first

                            for directory in dir_list: #When clicking or selecting a new subject, iterate through the subject directory and reconstruct the subfolder scroll area
                                self.context.scrollable_subfolders.refreshSubfolders(self.context, directory, widget_layout, 'Subfolder')

                        self.context.update_card_count(len(dir_list))
                        self.context.selectionArrowIndicator(self) #Check utilities for additional info
                
                elif area_type == 'Subfolder':
                    self.context.subtopic_path = self.context.subj_path / f"{self.name}"
                    self.context.isSubjectSelection = False #Toggle selection state for other functions that will use it
                    self.context.selectionArrowIndicator(self) #Check utilities for additional info
                    print(str(self.context.subtopic_path))

                if self.context.folder_popup.isVisible():
                    '''If a click is triggered and folder creation menu is visible, update the selection label for the said popup'''
                    self.context.folder_popup.update_parent_folder_display()

        def startReview(self, event):
            '''Modify and add the json file name to the data path'''
            if event.type() == QEvent.Type.MouseButtonDblClick:
                self.review_pane = cardReviewWindow(self.context)
                self.review_pane.show()

class createFolderPopup(QWidget):
    def __init__(self, context):
        super().__init__()
        self.setStyleSheet('background-color: #253463')
        self.context = context
        self.setWindowTitle("Folder Creation")
        self.setFixedSize(500, 300)
        self.setWindowModality(Qt.WindowModality.NonModal) #Dont block events and input from window behind popup

        self.setWindowFlags(
            Qt.WindowType.Tool | #Make it a tool window instead of QWidget
            Qt.WindowType.WindowStaysOnTopHint #Make the window stay on top
        )

        main_layout = QVBoxLayout()

        # Folder name input
        folder_name_label = QLabel('Folder Name: ')
        folder_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        folder_name_label.setStyleSheet('color: white; font-size: 30 px; font-weight: 500; font-family: Open Sans; border-radius: 6px; background-color: #b39f72')
        self.context.setShadow(folder_name_label, 3, 3, 5, 80)
        self.folder_name_input = QLineEdit()
        self.folder_name_input.setStyleSheet('background-color: #decfad; border-radius: 4px;')
        folder_input_layout = QHBoxLayout()
        folder_input_layout.addWidget(folder_name_label, stretch=2)
        folder_input_layout.addWidget(self.folder_name_input, stretch=8)
        main_layout.addLayout(folder_input_layout)

        # Radio buttons for Subject / Subtopic
        selection_type_label = QLabel('Select Folder Type')
        selection_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        selection_type_label.setStyleSheet('color: white; font-size: 18 px; font-weight: 500; font-family: Open Sans; border-radius: 6px; background-color: #b39f72')
        self.context.setShadow(selection_type_label, 3, 3, 5, 80)
        self.subject_radio = QRadioButton("New Subject")
        self.subtopic_radio = QRadioButton("New Subtopic")
        self.subject_radio.setChecked(True)  # default selection

        for radio_bn in [self.subject_radio, self.subtopic_radio]:
            radio_bn.setStyleSheet('color: white; font-family: Open Sans;')

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(selection_type_label)
        radio_layout.addWidget(self.subject_radio)
        radio_layout.addWidget(self.subtopic_radio)
        main_layout.addLayout(radio_layout)

        # Placeholder label for parent folder (shown only if subtopic is selected)
        self.parent_folder_label = QLabel("")
        self.parent_folder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.parent_folder_label.setStyleSheet('background-color: #141c36; border-radius: 8px; font-size: 30px; font-family: Open Sans; color: #fae2be;')
        main_layout.addWidget(self.parent_folder_label)

        self.subject_radio.toggled.connect(self.update_parent_folder_display)

        self.buttons_layout = QHBoxLayout()
        self.create_btn = QPushButton("➕📁 Create")
        self.create_btn.clicked.connect(self.createNewFolder)
        self.close_btn = QPushButton("❌ Close")
        self.close_btn.clicked.connect(self.hide)

        for button in [self.create_btn, self.close_btn]:
            button.setStyleSheet('background-color: #b39f72; border-radius: 4px; color: white;')

        self.buttons_layout.addWidget(self.create_btn)
        self.buttons_layout.addWidget(self.close_btn)

        main_layout.addLayout(self.buttons_layout)

        self.setLayout(main_layout)

    def update_parent_folder_display(self):
        """Update the placeholder text depending on the selected radio button."""
        if self.subject_radio.isChecked():
            self.parent_folder_label.setText("")

        if not self.subject_radio.isChecked() and self.context.currentSubtFolderSelection:
            self.parent_folder_label.setText(f"Current Selection Invalid!\nPlease Select a Subject Folder")
        elif self.subtopic_radio.isChecked():
            self.parent_folder_label.setText(f"Parent Folder: {self.context.selection_label.text().split(':')[1]}")
            self.context.isSubjectSelection = False
        else:
            self.parent_folder_label.setText("")
            self.context.isSubjectSelection = True
    
    def createNewFolder(self):
        if self.context.isSubjectSelection: path = self.context.prog_path / self.folder_name_input.text()
        else: path = self.context.subj_path / self.folder_name_input.text()

        try:
            os.makedirs(path, exist_ok=True)  # exist_ok=True avoids errors if folder exists
        except Exception as e:
            print(f"Error creating folder: {e}")

        if not self.context.isSubjectSelection: #Create a json file for a subtopic folder
            try:
                str_path = str(path / self.folder_name_input.text())
                with open(f'{str_path}.json', 'w'):
                    ...
            except FileExistsError: #If the json file already exists do not overwrite
                ...
            
        self.folder_name_input.clear() #Clear Input Field for Folder Name
        
        if self.context.isSubjectSelection: self.context.scrollable_subjects.createFolders(delete=True)
        else: self.context.scrollable_subfolders.createFolders(delete=True)

class cardOptionsPopup(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.setWindowTitle("Card Actions")
        self.setFixedSize(400, 100)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setStyleSheet("""
            QWidget {
                background: #f7d145;
            }
            QWidget:hover {
                background: orange;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px;
            }
        """)

        self.add_card_btn = QPushButton("Add Card")
        self.add_card_btn.clicked.connect(self.cardCreationScreen)
        self.delete_card_btn = QPushButton("Delete Card")
        self.edit_card_btn = QPushButton("Edit Card")

        layout = QHBoxLayout()
        layout.addWidget(self.add_card_btn)
        layout.addWidget(self.delete_card_btn)
        layout.addWidget(self.edit_card_btn)
        layout.setSpacing(20)
        self.setLayout(layout)

    def cardCreationScreen(self):
        self.hide()
        self.cardScreen = CardCreator()
        self.cardScreen.show()

class cardCountHelp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Card Number Help')
        self.setStyleSheet('background-color: #253463;')

        self.setWindowFlags(
            Qt.WindowType.Tool | #Make it a tool window instead of QWidget
            Qt.WindowType.WindowStaysOnTopHint | #Make the window stay on top
            Qt.WindowType.WindowCloseButtonHint
        )

        self.resize(300, 150)
        header = QLabel('📇#Cards (Next Session)')
        header.setStyleSheet('font-size: 25px; color: #fae2be;')
        description = QLabel("""
                    💳 The Total Number of Cards for Review on
                    the Next Session with the selected subtopics.

                    🔁 Spaced Repetition: The Cards shown per session is 
                    based on a date interval. This interval relies on 
                    your performance and ability to recall the card
                    during the previous review sessions.
                             """)
        description.setStyleSheet('color: #fae2be;')

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(description)

        self.setLayout(layout)

class folderHelpPopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Folder Help')
        self.setStyleSheet('background-color: #253463;')
        
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
