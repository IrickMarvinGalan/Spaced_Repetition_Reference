from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys
import shutil

from mainMenuWidgets import *
from utilities import *
from icon_downloader import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spaced Repetition")
        self.setMinimumSize(1350, 695)

        # Create context for shared references across widgets
        self.context = UIContext()

        #Check if user is new, create a folder in users/documents
        self.verifySpacedRep_Folder()

        #Check if icon resources is already downloaded
        self.verifyIconDownloads()

        # Layout setup
        self.layouts()
        self.mainMenuInterface()

    def layouts(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(15)

        self.center_widget = QWidget()
        self.center_widget.setStyleSheet('background-color: #7593bd;')
        self.center_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.center_widget)
        
        self.button_utils_layout = QHBoxLayout()
        self.button_utils_layout.setContentsMargins(50, 0, 50, 0)

        self.folder_pane_layout = QVBoxLayout()
        self.folder_pane_layout.setContentsMargins(0, 0, 0, 0)
        self.folder_pane_layout.setSpacing(0)

        self.folder_pane_wrap = QVBoxLayout()
        self.folder_pane_wrap.setContentsMargins(50, 0, 50, 30)
        self.folder_pane_wrap.addLayout(self.folder_pane_layout)

        self.folder_list_layout = QHBoxLayout()
        self.folder_list_layout.setContentsMargins(0, 0, 7, 0)
        self.folder_list_layout.setSpacing(5)

        self.subject_columns_layout = QHBoxLayout()
        self.subject_scroll_layout = QVBoxLayout() #The subjects scroll layout at startup

        self.subfolder_scroll_layout = QVBoxLayout() #The subfolders scroll layout at startup

    def mainMenuInterface(self):
        # ----- Title -----
        '''Initialize a separate widget for title to add shadow for header text'''
        title = QWidget()
        title.setMinimumWidth(1350)
        title_wrap = QHBoxLayout()
        title_wrap.addWidget(title)
        title_wrap.setContentsMargins(0, 0, 0, 0)
        self.context.setShadow(title, 0, 3, 10, 150) #Check utilities for additional info
        title_label = QLabel('🔁Spaced Repetition🔁')
        title_label.setStyleSheet('font-size: 70px; font-weight: 600; color: #f5efe6; letter-spacing: 2px;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)    

        title_layout = QHBoxLayout()
        title_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        title.setLayout(title_layout)
        self.main_layout.addLayout(title_wrap)

        # ----- Utility Buttons -----
        self.context.selection_label = QLabel('Selected Folder: None')
        self.context.selection_label.setStyleSheet('font-size: 20px; color: white;')
        self.context.add_folder = QPushButton('➕📂Add Folder')
        self.context.add_folder.clicked.connect(self.createNewFolder)
        self.context.del_folder = QPushButton('🗑️Delete Folder')
        self.context.del_folder.clicked.connect(self.deleteFolder)
        self.context.mod_folder = QPushButton('⚙️Modify Folder')
        self.context.mod_folder.clicked.connect(self.modifyFolder)
        self.context.review = QPushButton('📖Review')
        #self.context.review.clicked.connect(self.startReview)

        self.context.folder_popup = createFolderPopup(self.context) #Initialize popup for folder creation

        for button in (self.context.add_folder, self.context.mod_folder, self.context.review):
            button.setFixedSize(185, 60)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    font-weight: 600;
                    color: #6D94C5;
                    background: #e8dfca;
                    border-radius: 25px;
                    padding: 0px 10px 0px 10px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background: #d4cbb8;
                }
            """)

            self.context.setShadow(button, 3, 3, 15, 200)
        
        self.context.del_folder.setFixedSize(185, 60)
        self.context.del_folder.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    font-weight: 600;
                    color: #ffffff;
                    padding: 0px 10px 0px 10px;
                    margin: 0px;
                    background: #fc2d2d;
                    border-radius: 25px;
                }
                QPushButton:hover {
                    background: #f70202;
                }
            """)
    
        self.button_utils_layout.addWidget(self.context.add_folder)
        self.button_utils_layout.addWidget(self.context.del_folder)
        self.button_utils_layout.addWidget(self.context.mod_folder)
        self.button_utils_layout.addWidget(self.context.review)
        self.button_utils_layout.addSpacing(100)
        self.button_utils_layout.addWidget(self.context.selection_label)

        self.context.folderSelectionValidator('Subfolder')
        self.main_layout.addLayout(self.button_utils_layout)

        # ----- Folder Pane -----
        folder_pane_widget = QWidget() #Widget will be used for setting shadow over the scroll areas  
        folder_pane_widget.setStyleSheet('background-color: #ebe1d1;')
        folder_pane_widget.setLayout(self.folder_list_layout)

        self.context.setShadow(folder_pane_widget, 3, 3, 5, 80)

        subject_columns = QWidget()
        subject_columns.setFixedHeight(45)
        subject_columns.setMinimumWidth(1000)
        subject_columns.setStyleSheet('background-color: #f5efe6;')

        column_labels = ['Subject', '📁Subtopic Folders ❓', 'Card # (Next Session) ❓']
        column_stretch = [3, 6, 2]

        subjects_label = QLabel(column_labels[0])
        self.folders_help_popup = folderHelpPopup() #The popup that will display the message when pressing folder help
        folders_help_label = interactableLabel(column_labels[1], self.folders_help_popup)
        self.card_help_popup = cardCountHelp() #The popup that will display the help message for card count
        card_help_label = interactableLabel(column_labels[2], self.card_help_popup)

        subjects_label.setStyleSheet("""
                QWidget {
                    font-size: 18px; 
                    font-weight: 700; 
                    color: #6D94C5;
                }
            """)

        for label in [folders_help_label, card_help_label]:
            label.setStyleSheet("""
                QWidget {
                    border-radius: 10px;
                    background-color: #edddb9;
                    font-size: 18px; 
                    font-weight: 700; 
                    color: #6D94C5;
                }
                QLabel::hover {
                    background-color: #b3a68b;
                    border-radius: 10px;
                    color: black; 
                }
            """)

        self.subject_columns_layout.addWidget(subjects_label, stretch=column_stretch[0])
        self.subject_columns_layout.addWidget(folders_help_label, stretch=column_stretch[1], alignment=Qt.AlignmentFlag.AlignLeft)
        self.subject_columns_layout.addWidget(card_help_label, stretch=column_stretch[2], alignment=Qt.AlignmentFlag.AlignLeft)

        subject_columns.setLayout(self.subject_columns_layout)
        self.folder_pane_layout.addWidget(subject_columns) #Add the layout containing columns label to a spaceless layout to create table

        # Scroll Areas
        self.context.scrollable_subfolders = scrollArea(self.context, primary_layout=self.folder_list_layout, 
                                                        scroll_layout=self.subfolder_scroll_layout)
        self.context.scrollable_subjects = scrollArea(self.context, primary_layout=self.folder_list_layout, strch=3, 
                                                      scroll_layout=self.subject_scroll_layout, 
                                                      area_type='Subject')

        self.folder_list_layout.addWidget(self.context.scrollable_subfolders, stretch=6)

        # ----- Card Count Holder -----
        card_count = QWidget()
        card_count.setFixedSize(250, 250)
        card_count.setStyleSheet('background-color: #eddfbe; border-radius: 20px; border: 1px solid #555')
        card_count_layout = QHBoxLayout()
        card_count.setLayout(card_count_layout)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setOffset(3, 3)
        shadow.setColor(QColor(0, 0, 0, 80))
        card_count.setGraphicsEffect(shadow)

        self.context.card_count_label = QLabel('0')
        self.context.card_count_label.setStyleSheet('font-size: 60px; font-weight: 900; color: #6D94C5')
        self.context.card_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_count_layout.addWidget(self.context.card_count_label)

        self.folder_list_layout.addWidget(card_count, stretch=2, alignment=Qt.AlignmentFlag.AlignTop)
        self.folder_pane_layout.addWidget(folder_pane_widget)
        self.main_layout.addLayout(self.folder_pane_wrap)

    def createNewFolder(self):
        self.context.folder_popup.show()

    def deleteFolder(self):
        try:
            # Recursively delete the folder and its contents
            if self.context.isSubjectSelection: 
                shutil.rmtree(self.context.subj_path)
                self.context.scrollable_subjects.createFolders(delete=True)
                #Reset selection pointer when deleting a subject folder
                self.context.currentSubjFolderSelection = None
                self.context.prevSubjFolderSelection = None
                self.context.emptyScrollArea(self.context.scrollable_subfolders)
            else: 
                shutil.rmtree(self.context.subtopic_path)
                self.context.scrollable_subfolders.createFolders(delete=True)

            #Reset selection pointer when deleting a subtopic/subject folder
            self.context.currentSubtFolderSelection = None
            self.context.prevSubtFolderSelection = None
            
            self.context.selection_label.setText('Selected Folder: None')
            self.context.folderSelectionValidator()
            print(f"Folder deleted successfully")
        except Exception as e:
            print(f"Error deleting folder")
        
    def modifyFolder(self):
        self.cardOptions = cardOptionsPopup(self.context)
        self.cardOptions.show()

    def verifySpacedRep_Folder(self):
        """
        Creates a 'SpacedRep' folder inside the user's Documents directory
        if it's the user's first time using the app
        """
        documents_path = Path.home() / "Documents"
        spacedrep_path = documents_path / "SpacedRep"

        try:
            os.makedirs(spacedrep_path, exist_ok=True)
            print(f"'SpacedRep' directory ensured at: {spacedrep_path}")
        except Exception as e:
            print(f"Error creating 'SpacedRep' folder: {e}")
    
    def verifyIconDownloads(self):
        repo_url = f"https://github.com/IrickMarvinGalan/SpacedRep_IconResources.git"  # Link to the repository
        destination_folder = "C:\\Users\\GALAN\\Documents\\SpacedRep\\Resources"  # Destination for Icon Download

        clone_github_repo(repo_url, destination_folder)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont('Segoe UI')
    font.setStretch(85)
    font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 105)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
