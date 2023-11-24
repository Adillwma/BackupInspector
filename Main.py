from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QFileDialog, QListWidgetItem
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt6 import uic
import subprocess
import datetime
import filecmp
import hashlib
import shutil
import sys
import os
import time
import requests
import json


# Load in the resources file
import resources_rc

#%% - Backend 
class BackupInspectorClass:
    def __init__(self):
        pass

    def compare_directories(self, refrence_directory, target_directory):
        comparison = filecmp.dircmp(refrence_directory, target_directory, ignore=None)

        self.left_only_total += len(comparison.left_only)
        self.right_only_total += len(comparison.right_only)
        self.diff_files_total += len(comparison.diff_files)
        self.same_files_total += len(comparison.same_files)

        for filename in comparison.left_only:
            # check if it is a folder or a file
            if os.path.isdir(os.path.join(refrence_directory, filename)):
                # if it is a folder than calulate how many files are in it and in all of its subdirectories and add that to the left only total whilst also adding all the file names to the missing files list. for each folder and subfolder encotered remove one from the left only total as it is not a file
                self.left_only_total -= 1
                for root, dirs, files in os.walk(os.path.join(refrence_directory, filename)):

                    # add the number of files in the directory to the left only total
                    self.left_only_total += len(files)

                    # add the files in the directory to the missing files list
                    for file in files:
                        self.missing_files_list.append(os.path.join(root, file))

            else:
                # if it is a file then just add it to the missing files list
                self.missing_files_list.append(os.path.join(refrence_directory, filename))        # must be faster way to tdo this than looping through as it is just taking  alsit to another list and appending constant string to begibg of each entry in list, similarly below


        for filename in comparison.right_only:
            if os.path.isdir(os.path.join(target_directory, filename)):                # check if it is a folder or a file
                self.right_only_total -= 1                                             # remove one from the right only total as it is not a file


        if self.hash_choice != "None":                                    # PROBABLOY QUICKER TO REMOVE THIS AND JUST DIRECTLY DO HASH CHECK AT HIS POINT RATHER THAN AFTER ALL DIRECTORIES HAVE BEEN COMPARED
            for filename in comparison.same_files:  
                self.possible_match_list_refrence.append(os.path.join(refrence_directory,filename))            #append filenames of all same_files_total to possible_match_list for checksum scanning
                self.possible_match_list_target.append(os.path.join(target_directory,filename))              #append filenames of all same_files_total to possible_match_list for checksum scanning

        # Recursively compare subdirectories
        for subdirname in comparison.common_dirs:
            self.compare_directories(os.path.join(refrence_directory, subdirname), os.path.join(target_directory, subdirname))

    def calculate_hash(self, file_path):

        # Initialize MD5 or SHA-1 hash object.
        if self.hash_choice == "Md5":
            hash_operator = hashlib.md5()
        elif self.hash_choice == "Sha-1":
            hash_operator = hashlib.sha1()
        elif self.hash_choice == "Sha-256":
            hash_operator = hashlib.sha256()
        elif self.hash_choice == "Sha-3-256":
            hash_operator = hashlib.sha3_256()

        # Calculate hashes for the files
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(8192)  # Read data in chunks.
                if not data:
                    break
                hash_operator.update(data)

        return hash_operator.hexdigest()

    def checksum_comparison(self):
        # Iterate through the list of possible matches.
        for reference_path, target_path in zip(self.possible_match_list_refrence, self.possible_match_list_target):
            
            reference_hash = self.calculate_hash(reference_path)
            target_hash = self.calculate_hash(target_path)

            # If hashes DO NOT match
            if reference_hash != target_hash:
                # Add the reference path to the list of missing files.
                self.missing_files_list.append(reference_path)
                # add one to the count of diff files and one to the left only total
                self.diff_files_total += 1
                self.left_only_total += 1

                # remove the reference and target  paths from thier respective lists of possible matches
                self.possible_match_list_refrence.remove(reference_path)
                self.possible_match_list_target.remove(target_path)
                # remove one from the count of same files
                self.same_files_total -= 1

    def run(self, reference_dirs, target_dirs, hash_choice):
        self.hash_choice = hash_choice
        self.left_only_total = 0
        self.right_only_total = 0
        self.diff_files_total = 0
        self.same_files_total = 0
        self.possible_match_list_refrence = []
        self.possible_match_list_target = []
        self.missing_files_list = []

        for reference_directory, target_directory in zip(reference_dirs, target_dirs):
            self.compare_directories(reference_directory, target_directory)

        if hash_choice != "None":
            self.checksum_comparison()

        # Calculate the total number of files in the reference and target directories.
        total_files_reference = self.left_only_total + self.same_files_total
        total_files_target = self.right_only_total + self.same_files_total

        # Calculate the percentage of files missing from the target directory.
        percentage_missing = round((self.left_only_total / total_files_reference) * 100, 2)

        # Calculate the percentage of files that are the same between the reference and target directories.
        percentage_same = round((self.same_files_total / total_files_reference) * 100, 2)

        return self.left_only_total, self.right_only_total, self.diff_files_total, self.same_files_total, self.missing_files_list, total_files_reference, total_files_target, percentage_missing, percentage_same
    
def wrapper(reference_directory, target_directory, hash_choice):
        

    backup_inspector = BackupInspectorClass()
    left_only_total, right_only_total, diff_files_total, same_files_total, missing_files_list, total_files_reference, total_files_target, percentage_missing, percentage_same = backup_inspector.run(reference_directory, target_directory, hash_choice)

    #print(f"total_files_reference: {total_files_reference}")
    #print(f"total_files_target: {total_files_target}")
    #print(f"left_only_total: {left_only_total}")
    #print(f"right_only_total: {right_only_total}")
    #print(f"diff_files_total: {diff_files_total}")
    #print(f"same_files_total: {same_files_total}")
    #print(f"percentage_same: {percentage_same}")
    #print(f"percentage_missing: {percentage_missing}")
    #print(f"missing_files_list: {missing_files_list}")

    files_only_in_dir1 = left_only_total
    files_only_in_dir2 = right_only_total
    perfect_matches = same_files_total
    files_scanned_in_dir1 = total_files_reference
    files_scanned_in_dir2 = total_files_target
    percent_matched_dir1 = percentage_same


    return (
        files_scanned_in_dir1,
        files_scanned_in_dir2,
        perfect_matches,
        files_only_in_dir1,
        files_only_in_dir2,
        percent_matched_dir1,
        percentage_missing,
        missing_files_list

        )

def file_copier(reference_dirs, target_dirs, missing_files_list):

    for reference_dir, target_dir in zip(reference_dirs, target_dirs):

        # determine which of the missing files are in the current reference directory
        missing_files_list_chunk = [file for file in missing_files_list if reference_dir in file]

        for missing_file_path in missing_files_list_chunk:
            # Determine the relative path of the missing file within the reference directory
            relative_path = os.path.relpath(missing_file_path, reference_dir)

            # Construct the target file path
            target_file_path = os.path.join(target_dir, relative_path)

            # Ensure the target directory exists
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

            # Copy the missing file to the target directory
            shutil.copy(missing_file_path, target_file_path)



def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def wrap_text_with_template(input_text):
    template = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" /><style type="text/css">
    p, li { white-space: pre-wrap; }
    </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; ">
    <p align="justify" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">INSERT INPUT TEXT STRING HERE!</p></body></html>
    """
    return template.replace("INSERT INPUT TEXT STRING HERE!", input_text)



#%% - Front End UI
# Load the UI file
Form, Window = uic.loadUiType("interface.ui")
app = QApplication([])

## MAIN WINDOW CLASS
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Form()
        self.ui.setupUi(self)

        # Simple Customisation Settings
        self.online_version_file_link = "https://github.com/Adillwma/BackupInspector/raw/main/config.json"    # Make sure to use the raw link to the file, (you can swap the blob in the normal link to raw)
        self.update_download_link = "https://github.com/Adillwma/BackupInspector/raw/main/BackupInspector.exe"

        self.config_file = 'App_Data\config.json'
        self.check_preferences()          # Checks the user preferences file to load the correct settings

        self.help_text_path = resource_path(r"App_Data\copy\help_text.txt")
        self.info_text_path = resource_path(r"App_Data\copy\info_text.txt")

        ### Initialise UI Elements
        self.init_modularUI()           # Modular Unified Ui
        self.init_programUI()           # Main Program Ui elements

    #%% - Initialise Ui Elements
    def init_modularUI(self):

        # Left Menu
        self.left_menu_animation = QPropertyAnimation(self.ui.leftMenuContainer, b"maximumWidth")
        self.left_menu_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.left_menu_animation.setDuration(1000)  # Animation duration in milliseconds
        self.ui.leftMenuBtn_UiBtnType.clicked.connect(self.expandorshrink_left_menu)
        self.highlightedLeftMenuBtn = self.ui.homeBtn_UiBtnType
        #self.ui.leftMenuContainer.setMaximumWidth(50)   # start with left menu shrunk by setting max width to 50

        self.ui.homeBtn_UiBtnType.clicked.connect(lambda: self.handle_left_menu(page=self.ui.homePage, button=self.ui.homeBtn_UiBtnType))
        self.ui.reportBtn_UiBtnType.clicked.connect(lambda: self.handle_left_menu(page=self.ui.reportPage, button=self.ui.reportBtn_UiBtnType))
        self.ui.settingsBtn_UiBtnType.clicked.connect(lambda: self.handle_centre_menu(page=self.ui.settingsCenterMenuPage))
        self.ui.infoBtn_UiBtnType.clicked.connect(lambda: self.handle_centre_menu(page=self.ui.infoCenterMenuPage))
        self.ui.helpBtn_UiBtnType.clicked.connect(lambda: self.handle_centre_menu(page=self.ui.helpCenterMenuPage))

        # Center Menu
        self.center_menu_animation = QPropertyAnimation(self.ui.centerMenuContainer, b"maximumWidth")
        self.center_menu_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.center_menu_animation.setDuration(1000)  # Animation duration in milliseconds
        self.ui.centerMenuCloseBtn_UiBtnType.clicked.connect(lambda: self.run_animation(self.center_menu_animation, start=250, end=5))
        self.ui.centerMenuContainer.setMaximumWidth(5)         # Set centre menu to start hidden (with max width of 0)   

        
        # Notification Container
        self.notification_animation = QPropertyAnimation(self.ui.popupNotificationContainer, b"maximumHeight")
        self.notification_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.notification_animation.setDuration(1000)
        self.ui.notificationCloseBtn_UiBtnType.clicked.connect(lambda: self.run_animation(self.notification_animation, start=100, end=0))
        self.ui.popupNotificationContainer.setMaximumHeight(0)  # Set notification container to start hidden (with max height of 0)

        # ui theme dark / light
        self.dark_mode_path = resource_path(fr"themes\{self.current_theme}\dark_mode.css")
        self.light_mode_path = resource_path(fr"themes\{self.current_theme}\light_mode.css")
        self.current_ui_mode = "dark"
        self.highlight_theme_color = "background-color: #1f232a;"
        self.ui.uiThemeBtn_UiBtnType.clicked.connect(self.switch_ui_mode)
        self.init_icons()
        self.set_theme()

        ### SETTINGS PAGE
        self.ui.themesListSelector.currentTextChanged.connect(self.set_theme)
        self.ui.checkForUpdates_ProgramBtnType.clicked.connect(self.check_online_for_updates)
        self.ui.downloadUpdateBtn_ProgramBtnType.clicked.connect(self.download_latest_version)

        ### HELP & INFO PAGES
        self.set_helpandinfo_copy(self.help_text_path, self.info_text_path)

    def init_programUI(self):
        # Settings page
        self.ui.hashTypeSelector.currentTextChanged.connect(self.set_hash_method)
        self.hash_choice = 'None'

        # Backend Variables
        self.selected_directories1 = []
        self.selected_directories2 = []
        self.list1 = self.ui.list1
        self.list2 = self.ui.list2

        # Home Page
        self.ui.pushButton_2_ProgramBtnType.clicked.connect(self.add_folder)
        self.ui.pushButton_3_ProgramBtnType.clicked.connect(self.run_backupinspector)
        self.ui.pushButton_4_ProgramBtnType.clicked.connect(self.add_folder2)
        self.ui.pushButton_5_ProgramBtnType.clicked.connect(self.delete_folder)
        self.ui.pushButton_6_ProgramBtnType.clicked.connect(self.delete_folder2)
        self.ui.saveConfig_ProgramBtnType.clicked.connect(self.save_config_to_disk)
        self.ui.loadConfig_ProgramBtnType.clicked.connect(self.load_config_from_disk)
        self.ui.useChecksumCheckbox.stateChanged.connect(self.set_hash_method)
        self.ui.recoverMissingFiles_ProgramBtnType.clicked.connect(self.copy_all_missing_files)
        self.ICON_RED_LED = QPixmap(resource_path(r"Icons\LEDs\led-red-on.png"))
        self.ICON_BLUE_LED = QPixmap(resource_path(r"Icons\LEDs\blue-led-on.png"))
        self.ICON_GREEN_LED = QPixmap(resource_path(r"Icons\LEDs\green-led-on.png"))

        # Report Page
        self.ui.viewReportPage_ProgramBtnType.clicked.connect(lambda: self.handle_left_menu(page=self.ui.reportPage, button=self.ui.reportBtn_UiBtnType))
        self.ui.show_report_txt_ProgramBtnType.clicked.connect(self.show_results_txt)
        self.ui.recoverMissingFiles2_ProgramBtnType.clicked.connect(self.copy_all_missing_files)

    #%% - Modular Ui Functions
    def init_icons(self):
        
        self.iconw = QIcon()
        self.iconb = QIcon()
        self.iconw.addPixmap(QPixmap(":/whiteicons/icons/light/align-justify.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.iconb.addPixmap(QPixmap(":/blackicons/icons/dark/align-justify.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon1w = QIcon()
        self.icon1b = QIcon()
        self.icon1w.addPixmap(QPixmap(":/whiteicons/icons/light/home.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon1b.addPixmap(QPixmap(":/blackicons/icons/dark/home.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon2sw = QIcon()
        self.icon2sb = QIcon()
        self.icon2sw.addPixmap(QPixmap(":/whiteicons/icons/light/trending-up.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon2sb.addPixmap(QPixmap(":/blackicons/icons/dark/trending-up.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon2w = QIcon()
        self.icon2b = QIcon()
        self.icon2w.addPixmap(QPixmap(":/whiteicons/icons/light/printer.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon2b.addPixmap(QPixmap(":/blackicons/icons/dark/printer.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon3w = QIcon()
        self.icon3b = QIcon()
        self.icon3w.addPixmap(QPixmap(":/whiteicons/icons/light/settings.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon3b.addPixmap(QPixmap(":/blackicons/icons/dark/settings.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon4w = QIcon()
        self.icon4b = QIcon()
        self.icon4w.addPixmap(QPixmap(":/whiteicons/icons/light/info.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon4b.addPixmap(QPixmap(":/blackicons/icons/dark/info.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon5w = QIcon()
        self.icon5b = QIcon()
        self.icon5w.addPixmap(QPixmap(":/whiteicons/icons/light/help-circle.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon5b.addPixmap(QPixmap(":/blackicons/icons/dark/help-circle.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon6w = QIcon()
        self.icon6b = QIcon()
        self.icon6w.addPixmap(QPixmap(":/whiteicons/icons/light/x-circle.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon6b.addPixmap(QPixmap(":/blackicons/icons/dark/x-circle.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon7w = QIcon()
        self.icon7b = QIcon()
        self.icon7w.addPixmap(QPixmap(":/whiteicons/icons/light/more-horizontal.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon7b.addPixmap(QPixmap(":/blackicons/icons/dark/more-horizontal.svg"), QIcon.Mode.Normal, QIcon.State.Off)

        self.icon8w = QIcon()
        self.icon8b = QIcon()
        self.icon8w.addPixmap(QPixmap(":/whiteicons/icons/light/sun.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon8b.addPixmap(QPixmap(":/blackicons/icons/dark/moon.svg"), QIcon.Mode.Normal, QIcon.State.Off)

    def set_icons_white(self):
        self.ui.leftMenuBtn_UiBtnType.setIcon(self.iconw)
        self.ui.homeBtn_UiBtnType.setIcon(self.icon1w)
        self.ui.reportBtn_UiBtnType.setIcon(self.icon2w)
        self.ui.settingsBtn_UiBtnType.setIcon(self.icon3w)
        self.ui.infoBtn_UiBtnType.setIcon(self.icon4w)
        self.ui.helpBtn_UiBtnType.setIcon(self.icon5w)
        self.ui.centerMenuCloseBtn_UiBtnType.setIcon(self.icon6w)
        self.ui.notificationCloseBtn_UiBtnType.setIcon(self.icon6w)

    def set_icons_black(self):
        self.ui.leftMenuBtn_UiBtnType.setIcon(self.iconb)
        self.ui.homeBtn_UiBtnType.setIcon(self.icon1b)
        self.ui.reportBtn_UiBtnType.setIcon(self.icon2b)
        self.ui.settingsBtn_UiBtnType.setIcon(self.icon3b)
        self.ui.infoBtn_UiBtnType.setIcon(self.icon4b)
        self.ui.helpBtn_UiBtnType.setIcon(self.icon5b)
        self.ui.centerMenuCloseBtn_UiBtnType.setIcon(self.icon6b)
        self.ui.notificationCloseBtn_UiBtnType.setIcon(self.icon6b)

    def check_preferences(self):
        # Load data from the config file
        with open(self.config_file, 'r') as file:
            self.config_data = json.load(file)

        # set the version number for checking for updates
        self.version_number = self.config_data["Version"]

        # set the default theme
        self.current_theme = self.config_data["Theme"]
        self.ui.themesListSelector.setCurrentText(self.current_theme) 

        # set the default ui mode
        #self.current_ui_mode = self.config_data["UI"]

    def run_animation(self, animation_item, start, end):
        animation_item.setStartValue(start)
        animation_item.setEndValue(end)
        animation_item.start()

    def handle_left_menu(self, page, button):
        # set the correct button to be highlighted using background-color: #1f232a; in stylesheet from the previous to the new page
        self.highlightedLeftMenuBtn.setStyleSheet("")
        self.highlightedLeftMenuBtn = button
        self.highlightedLeftMenuBtn.setStyleSheet(self.highlight_theme_color)

        # set the correct page to be displayed in mainContentPagesStack
        self.ui.mainContentPagesStack.setCurrentWidget(page)

    def expandorshrink_left_menu(self):
        # If the left menu is closed (width = 40), then it is opened
        if self.ui.leftMenuContainer.maximumWidth() == 50:
            self.run_animation(self.left_menu_animation, start=50, end=250)
        else:
            self.run_animation(self.left_menu_animation, start=250, end=50)

    def handle_centre_menu(self, page):
        # if the button pressed is the same as the current page and the menu is open then close the center menu
        if self.ui.centerMenuPagesStack.currentWidget() == page and self.ui.centerMenuContainer.maximumWidth() != 5:
            self.run_animation(self.center_menu_animation, start=250, end=5)  
        else:
            # If the center menu is closed (width = 5), then it is opened
            if self.ui.centerMenuContainer.maximumWidth() == 5:
                self.run_animation(self.center_menu_animation, start=5, end=250)

            # The correct center menu page is set for centerMenuPagesStack
            self.ui.centerMenuPagesStack.setCurrentWidget(page)

    def set_helpandinfo_copy(self, help_file_path, info_file_path):
        with open(help_file_path, "r") as file:
            self.ui.helpTextCopy.setText(self.ui.helpTextCopy.toHtml().replace("Help file failed to load. Sorry for the mix-up, we are scrambling to fix it!", file.read()))

        with open(info_file_path, "r") as file:
            self.ui.infoTextCopy.setText(self.ui.infoTextCopy.toHtml().replace("Information file failed to load. Sorry for the mix-up, we are scrambling to fix it!", file.read()))

    def set_theme(self):
        '''Sets the theme of the UI based on the selected theme in the themesListSelector'''

        # Get the selected theme from the themesListSelector
        selected_theme = self.ui.themesListSelector.currentText()

        # Set the current theme to the selected theme
        self.current_theme = selected_theme

        self.dark_mode_path = resource_path(fr"themes\{self.current_theme}\dark_mode.css")
        self.light_mode_path = resource_path(fr"themes\{self.current_theme}\light_mode.css")

        #switch to the new css based on the previos mode i.e dark/light
        if self.current_ui_mode == "dark":
            with open(self.dark_mode_path, "r") as file:
                self.setStyleSheet(file.read())
        else:
            with open(self.light_mode_path, "r") as file:
                self.setStyleSheet(file.read())

        # Save the current theme as default startup theme in the config JSON file
        with open(self.config_file, 'r') as file:
            data = json.load(file)

        data["Theme"] = self.current_theme   # Update the "Theme" value

        with open(self.config_file, 'w') as file:
            json.dump(data, file)  





    def switch_ui_mode(self):
        if self.current_ui_mode == "light":
            with open(self.dark_mode_path, "r") as file:
                self.setStyleSheet(file.read())
            self.current_ui_mode = "dark"
            self.highlight_theme_color = "background-color: #1f232a;"
            self.highlightedLeftMenuBtn.setStyleSheet(self.highlight_theme_color)
            self.set_icons_white()

        elif self.current_ui_mode == "dark":
            with open(self.light_mode_path, "r") as file:
                self.setStyleSheet(file.read())
            self.current_ui_mode = "light"
            self.highlight_theme_color = "background-color: #e4e7ec;"
            self.highlightedLeftMenuBtn.setStyleSheet(self.highlight_theme_color)
            self.set_icons_black()

    def check_online_for_updates(self):
        '''Checks online for updates and displays a notification if there is one'''

        # Get the latest version from the github repo json file
        response = requests.get(self.online_version_file_link)    # Send an HTTP GET request to the .JSON URL
        if response.status_code == 200:   # Verify request was successful (HTTP status code 200)
            text_content = response.text   # Read the response into a text string
        else:
            self.ui.popupNotificationText.setText(f"Unable to check for updates. HTTP status code: {response.status_code}")   # Report HTTP error and code
            self.run_animation(self.notification_animation, start=0, end=100)
            return
        
        latest_config_data = json.loads(text_content) # load as json data with 'loads' for string
        
        latest_version = latest_config_data["Version"]
        latest_version_int = int(''.join(latest_version.split('.')))

        current_version_int = int(''.join(self.version_number.split('.')))

        if current_version_int < latest_version_int:
            self.ui.popupNotificationText.setText(f"New version available: {latest_version}, please download update")
            self.run_animation(self.notification_animation, start=0, end=100)
            self.ui.downloadUpdateBtn_ProgramBtnType.setEnabled(True)   # Enable the update button

        else:
            self.ui.popupNotificationText.setText("You are using the latest version!")
            self.run_animation(self.notification_animation, start=0, end=100)

    def download_latest_version(self):
        # open link in users default browser
        os.startfile(self.update_download_link)

    #%% - Main Program Functions
    def update_list1(self):
        self.list1.clear()
        for directory in self.selected_directories1:
            item = QListWidgetItem(directory)
            self.list1.addItem(item)
        self.change_run_button_state()

    def update_list2(self):
        self.list2.clear()
        for directory in self.selected_directories2:
            item = QListWidgetItem(directory)
            self.list2.addItem(item)
        self.change_run_button_state()

    def add_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directories")
        if directory:
            self.selected_directories1.append(directory)
            self.update_list1()

    def add_folder2(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directories")
        if directory:
            self.selected_directories2.append(directory)
            self.update_list2()

    def delete_folder(self):
        for item in self.list1.selectedItems():
            self.selected_directories1.remove(item.text())
            self.list1.takeItem(self.list1.row(item))
        self.change_run_button_state()
 
    def delete_folder2(self):
        for item in self.list2.selectedItems():
            self.selected_directories2.remove(item.text())
            self.list2.takeItem(self.list2.row(item))
        self.change_run_button_state()
    
    # function to toggle led's state based on results
    def update_led(self):
        number = self.files_scanned_1 - self.num_perfect_matches
        if number == 0:
            self.ui.feedback_led.setPixmap(self.ICON_GREEN_LED)
        else:
            self.ui.feedback_led.setPixmap(self.ICON_RED_LED)

    def update_results(self):
        # update a qlcdnumber widgets with the number of files scanned
        self.ui.scanned_files_readoutcount.display(self.files_scanned_1)
        self.ui.missing_files_readoutcount.display(self.files_scanned_1 - self.num_perfect_matches)

        if self.files_scanned_1 - self.num_perfect_matches == 0:
            self.ui.test_status_text.setText("TEST: PASSED")
        else:
            self.ui.test_status_text.setText("TEST: FAILED")
        # enable the show report button
        #self.ui.show_report_txt_ProgramBtnType.setEnabled(True)
        self.ui.viewReportPage_ProgramBtnType.setEnabled(True)




        #### REPORT PAGE UPDATE ####
        self.ui.refFilesNumberReadout.display(self.files_scanned_1)
        self.ui.targetFilesNumberReadout.display(self.files_scanned_2)
        self.ui.percentMatchedReadout.setText(f"{self.percent_matched_dir1}%")
        self.ui.percentMissingReadout.setText(f"{self.percentage_missing}%")
        self.ui.missingNumberReadout.setText(f"{self.files_scanned_1 - self.num_perfect_matches}")
        self.ui.matchedNumberReadout.setText(f"{self.num_perfect_matches}")

        self.update_rotary_color_wheels()

        self.ui.reportMissingFileList.clear()
        for file in self.missing_files_list:
            item = QListWidgetItem(file)
            self.ui.reportMissingFileList.addItem(item)

    def update_rotary_color_wheels(self):
        # convert percentages to decimal values
        percent_good = self.percent_matched_dir1 / 100
        percent_bad = 1 - percent_good

        # calculate the stop values for the color gradients as +- 5% of the percentages but cliped to min 0 and max 1
        if percent_good >= 1.0:
            self.ui.filesfoundRadialColorWheel.setStyleSheet(f"background-color: rgba(7, 255, 119, 1);\nborder: 1px solid rgb(33, 24, 94);\nborder-radius: 60;")

        elif percent_good <= 0.0:
            self.ui.filesfoundRadialColorWheel.setStyleSheet(f"background-color: rgba(29, 21, 83, 1);\nborder: 1px solid rgb(33, 24, 94);\nborder-radius: 60;")
        else:
            green_stop1 = max(0, percent_good - 0.10)
            green_stop2 = min(1, percent_good + 0.05)
            self.ui.filesfoundRadialColorWheel.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:{green_stop1} rgba(7, 255, 119, 1), stop:{green_stop2} rgba(29, 21, 83, 1));\nborder: 1px solid rgb(33, 24, 94);\nborder-radius: 60;")
        
        if percent_bad >= 1.0:
            self.ui.filesmissingRadialColorWheel.setStyleSheet(f"background-color: rgba(255, 17, 80, 1);\nborder: 1px solid rgb(33, 24, 94);\nborder-radius: 60;")

        elif percent_bad <= 0.0:
            self.ui.filesmissingRadialColorWheel.setStyleSheet(f"background-color: rgba(29, 21, 83, 1);\nborder: 1px solid rgb(33, 24, 94);\nborder-radius: 60;")

        else:
            red_stop2 = 1 - max(0, percent_bad - 0.10)
            red_stop1 = 1 - min(1, percent_bad + 0.05)
            self.ui.filesmissingRadialColorWheel.setStyleSheet(f"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:{red_stop1} rgba(29, 21, 83, 1), stop:{red_stop2} rgba(255, 17, 80, 1));\nborder: 1px solid rgb(33, 24, 94);\nborder-radius: 60;")


    def show_results_txt(self):
        # find temp directory
        temp_dir = os.environ.get("TEMP")
        if temp_dir is None:
            temp_dir = os.environ.get("TMP")
        if temp_dir is None:
            temp_dir = os.environ.get("TMPDIR")
        if temp_dir is None:
            temp_dir = os.environ.get("TEMPDIR")
        if temp_dir is None:
            temp_dir = os.getcwd() # current working directory as fallback

        # Create a text file to write the results
        file_path = f'{temp_dir}\BackupInspector_results_{datetime.datetime.now().strftime("%d-%m-%Y")}.txt'

        with open(file_path, "w", encoding="utf-8") as f:
            # Write the title of the file as BACKUPINSPECTOR RESULTS
            f.write("BACKUPINSPECTOR RESULTS\n")

            # Add the date and time of the scan
            f.write(f"Scan date: {datetime.datetime.now()}\n")

            # Write the number of files scanned in total for the refrence dirs (dir1)
            f.write(f"\nFiles scanned in refrence dirs: {self.files_scanned_1}\n")

            # Write the number of files scanned in total for the target dirs (dir2)
            f.write(f"Files scanned in target dirs: {self.files_scanned_2}\n")

            # Write the number of perfect matches
            f.write(f"Number of perfect matches: {self.num_perfect_matches}\n")

            # Write number of files in refrence dirs (dir1) that are not in target dirs (dir2)
            f.write(f"Files in reference not in target: {self.num_files_only_in_dir1}\n")

            # Write number of files in target dirs (dir2) that are not in refrence dirs (dir1)
            f.write(f"Files in target not in reference: {self.num_files_only_in_dir2}\n\n\n")

            # Write list of the file names of the files that are only in dir1
            f.write("\n### Files missing from Target:\n")
            for file in self.missing_files_list:
                f.write(f"\n# {file}\n")


        # Open the file in Notepad 
        subprocess.Popen(["notepad.exe", file_path])   # Subprocess so as not to block the rest of the program

    # function to copy all missing files to target
    def copy_all_missing_files(self):
        self.run_animation(self.notification_animation, start=0, end=100)    # raise the notification popup
        file_copier(self.selected_directories1, self.selected_directories2, self.missing_files_list)
        self.run_animation(self.notification_animation, start=100, end=0)    # lower the notification popup

    def save_config_to_disk(self):
        # save the reference and target directories lists to a text file 
        with open("config.txt", "w") as file:
            for directory in self.selected_directories1:
                file.write(f"{directory}\n")
            file.write("###\n")
            for directory in self.selected_directories2:
                file.write(f"{directory}\n")

    def load_config_from_disk(self):
        # load the reference and target directories lists from a text file and add them to the list widgets
        self.selected_directories1 = []
        self.selected_directories2 = []
        with open("config.txt", "r") as file:
            for line in file:
                if line == "###\n":
                    break
                else:
                    self.selected_directories1.append(line.strip())
            for line in file:
                self.selected_directories2.append(line.strip())
        self.update_list1()
        self.update_list2()
        
    def set_hash_method(self):
        hash_type = self.ui.hashTypeSelector.currentText()
        if self.ui.useChecksumCheckbox.isChecked():
            self.hash_choice = hash_type
        else:
            self.hash_choice = "None"

    def change_run_button_state(self):
        if self.selected_directories1 and self.selected_directories2:
            self.ui.pushButton_3_ProgramBtnType.setEnabled(True)
        else:
            self.ui.pushButton_3_ProgramBtnType.setEnabled(False)

    def run_backupinspector(self):
        #self.ui.popupNotificationContainer.setMaximumHeight(100)
        #self.run_animation(self.notification_animation, start=100, end=100)    # lower the notification popup
        self.files_scanned_1, self.files_scanned_2, self.num_perfect_matches, self.num_files_only_in_dir1, self.num_files_only_in_dir2, self.percent_matched_dir1, self.percentage_missing, self.missing_files_list = wrapper(self.selected_directories1, self.selected_directories2, self.hash_choice)
        
        self.update_led()
        self.update_results()
        self.ui.reportBtn_UiBtnType.setEnabled(True)
        #self.run_animation(self.notification_animation, start=100, end=0)    # lower the notification popup







#%% - Run Program
if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

