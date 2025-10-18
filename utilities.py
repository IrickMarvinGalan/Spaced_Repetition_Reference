from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class UIContext:
    def __init__(self):
        self.selection_label = None
        self.add_folder = None
        self.del_folder = None
        self.mod_folder = None
        self.review = None
        self.isSubjectSelection = True #Checks if selected path is a subject for radio button and delete controls
        self.scrollable_subjects = None
        self.scrollable_subfolders = None
        self.card_count_label = None
        self.folder_popup = None

        #For Tracking the Arrow Marker for Subject Folder Selection
        self.currentSubjFolderSelection = None
        self.prevSubjFolderSelection = None

        #For Tracking the Arrow Marker for Subtopic Folder Selection
        self.currentSubtFolderSelection = None
        self.prevSubtFolderSelection = None

        #Path Info based on Selection
        self.prog_path = Path.home() / "Documents" / "SpacedRep"
        self.subj_path = None
        self.subtopic_path = None

    def emptyScrollArea(self, scrollArea):
        '''A helper function for resetting scroll Area when deleting folders
           Takes in the scrollArea reference and checks its area type to determine
           What selection pointers it should reset. Executes when delete=True
        '''
        if scrollArea.area_type == 'Subject':
            self.currentSubjFolderSelection = None
            self.prevSubjFolderSelection = None
            self.currentSubtFolderSelection = None
            self.prevSubtFolderSelection = None
        elif scrollArea.area_type == 'Subfolder':
            self.currentSubtFolderSelection = None
            self.prevSubtFolderSelection = None

        widget = scrollArea.widget()
        widget.deleteLater()

        widget = QWidget()
        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(2, 2, 2, 2)
        widget.setLayout(widget_layout)
        scrollArea.setWidget(widget)
        return widget_layout
    
    def setShadow(self, widget, x, y, rad, alpha):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(rad) #How sharp the edges of the shadow are
        shadow.setOffset(x, y) #The x and y displacement of the shadow
        shadow.setColor(QColor(0, 0, 0, alpha)) #Alpha inidicates the strength of the shadow
        widget.setGraphicsEffect(shadow)

    def styleFolders(self, folder, ftype):
        if ftype == 'Subject':
            folder.setStyleSheet("""
                    QWidget {
                        background: #e3bf8f;
                        border-radius: 20px;
                    }
                    QWidget:hover {
                        background: #b39f72;
                    }
                """)
        elif ftype == 'Subfolder':
            folder.setStyleSheet("""
                QWidget {
                    background: #decfad;
                    border-radius: 20px;
                }
                QWidget:hover {
                    background: #bdb093;
                }
            """)

    def selectionArrowIndicator(self, folder):
        if folder.area_type == 'Subject' and not self.currentSubjFolderSelection: #Condition is fulfilled upon first selection, or subsequent selections after deletion
            self.subjectSelectionColor(folder)

            #Set both previous and current to the selected folder as no previous selection is present
            self.currentSubjFolderSelection = folder
            self.currentSubjFolderSelection.label.setText(f'▶️ {self.selection_label.text().split(':')[1].strip()}')
            self.prevSubjFolderSelection = self.currentSubjFolderSelection

        elif folder.area_type == 'Subject' and self.currentSubjFolderSelection:
            if self.currentSubjFolderSelection == folder: return #If selecting the same folder do not do anything

            self.subjectSelectionColor(folder) #Style the folder for selection first. The function is unselect=False by default
            
            self.prevSubjFolderSelection = self.currentSubjFolderSelection #Save previous selection first
            self.currentSubjFolderSelection = folder #Set the new selected folder to the current
            self.subjectSelectionColor(self.prevSubjFolderSelection, unselect=True) #Return the previous selection to its original and unselected style

            self.currentSubjFolderSelection.label.setText(f'▶️ {self.selection_label.text().split(':')[1].strip()}') #Add arrow indicator for selection
            self.prevSubjFolderSelection.label.setText(self.prevSubjFolderSelection.label.text().split('▶')[1].strip()) #Remove arrow indicator for disselection

            '''Since a new subject was selected, the pointers containing the addresses of the previously selected subtopics no longer exist
               Ensure that subtopic pointers are reset to none to avoid referencing deleted objects causing runtime error
            '''
            self.prevSubtFolderSelection = None
            self.currentSubtFolderSelection = None
        
        elif folder.area_type == 'Subfolder' and not self.currentSubtFolderSelection:
            self.subjectSelectionColor(folder)

            self.currentSubtFolderSelection = folder
            self.currentSubtFolderSelection.label.setText(f'▶️ {self.selection_label.text().split(':')[1].strip()}')
            self.prevSubtFolderSelection = self.currentSubtFolderSelection
        
        elif folder.area_type == 'Subfolder' and self.currentSubtFolderSelection:
            if self.currentSubtFolderSelection == folder: return #Include error check for selecting the same folder

            self.subjectSelectionColor(folder) #Style the folder for selection first. The function is unselect=False by default
            
            self.prevSubtFolderSelection = self.currentSubtFolderSelection #Save previous selection first
            self.currentSubtFolderSelection = folder #Set the new selected folder to the current
            self.subjectSelectionColor(self.prevSubtFolderSelection, unselect=True)  #Return the previous selection to its original and unselected style

            self.currentSubtFolderSelection.label.setText(f'▶️ {self.selection_label.text().split(':')[1].strip()}') #Add arrow indicator for selection
            self.prevSubtFolderSelection.label.setText(self.prevSubtFolderSelection.label.text().split('▶')[1].strip()) #Remove arrow indicator for disselection

    def subjectSelectionColor(self, folder, unselect=False):
        if unselect:
                self.styleFolders(folder, folder.area_type) #If deselecting a folder set its style to the original whether its Subject or Subtopic
        else: #Style for selected folders, darkens color and removes the change of color when hovering
            folder.setStyleSheet("""
                    QWidget {
                        background: #b39f72;
                        border-radius: 20px;
                    }
                """)

    def folderSelectionValidator(self, area_type=None):
        """Enable/disable folder buttons depending on selection"""
        # Disable the delete, modify, and review buttons at startup
        for button in (self.del_folder, self.mod_folder, self.review):
            if button:
                opacity = QGraphicsOpacityEffect()
                opacity.setOpacity(0.3)
                button.setDisabled(True)
                button.setGraphicsEffect(opacity)

        # Validation: If no valid selection, exit early
        if not self.selection_label or self.selection_label.text() == 'Selected Folder: None':
            return

        # Enable based on selection type
        if area_type == 'Subject':
            # Enable Add and Delete; Disable Modify for Subject
            opacities = []
            for i in range (0, 4): #Create 4 graphics opacity effect to be modified based on enable/disable status
                opac = QGraphicsOpacityEffect()
                opacities.append(opac)

            for i in range (0, 4):
                if i in [0, 1]: #Enabled Opacities
                    opacities[i].setOpacity(0.85)
                elif i in [2, 3]: #Disabled Opacities
                    opacities[i].setOpacity(0.3)

            if self.add_folder: 
                self.add_folder.setEnabled(True)
                self.add_folder.setGraphicsEffect(opacities[0])

            if self.del_folder: 
                self.del_folder.setEnabled(True)
                self.del_folder.setGraphicsEffect(opacities[1])

            if self.mod_folder: 
                self.mod_folder.setDisabled(True)
                self.mod_folder.setGraphicsEffect(opacities[2])

            if self.review: 
                self.review.setDisabled(True)
                self.review.setGraphicsEffect(opacities[3])

        elif area_type == 'Subfolder':
            # Enable Modify and Delete; Disable Add for Subfolder
            # Enable Add and Delete; Disable Modify for Subject
            opacities = []

            for i in range (0, 4):
                opac = QGraphicsOpacityEffect()
                opacities.append(opac)

            for i in range (0, 4):
                if i in [0, 1, 2]: #Enabled Opacities
                    opacities[i].setOpacity(0.85)
                elif i == 3: #Disabled Opacities
                    opacities[i].setOpacity(0.3)

            if self.add_folder: 
                self.add_folder.setDisabled(True)
                self.add_folder.setGraphicsEffect(opacities[3])

            if self.del_folder: 
                self.del_folder.setEnabled(True)
                self.del_folder.setGraphicsEffect(opacities[0])

            if self.mod_folder: 
                self.mod_folder.setEnabled(True)
                self.mod_folder.setGraphicsEffect(opacities[1])

            if self.review: 
                self.review.setEnabled(True)
                self.review.setGraphicsEffect(opacities[2])

    def update_card_count(self, count: int):
        """Update card count label dynamically"""
        if self.card_count_label:
            self.card_count_label.setText(str(count))