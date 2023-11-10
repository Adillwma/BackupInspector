import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve 
from PyQt6 import uic
import resources_rc
import os

from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QApplication, QMainWindow
from PyQt6.QtGui import QPixmap
import shutil



#%% - Backend 
import os
import datetime
import subprocess

def file_generator(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            #yield os.path.join(root, file)  # Yield the full file path
            yield file  # Yield only the filename

def compare_directories(reference_dirs, target_dirs):
    set1 = set()
    set2 = set()
    set_dir1 = set()  # Initialize set for directory paths
    set_dir2 = set()  # Initialize set for directory paths

    for dir1 in reference_dirs:
        gen1 = file_generator(dir1)
        for file1 in gen1:
            set1.add(os.path.basename(file1))  # Add only the filename to set1
            set_dir1.add(file1)  # Add the full path to set_dir1

    for dir2 in target_dirs:
        gen2 = file_generator(dir2)
        for file2 in gen2:
            set2.add(os.path.basename(file2))  # Add only the filename to set2
            set_dir2.add(file2)  # Add the full path to set_dir2


    files_scanned_in_dir1 = len(set1)
    files_scanned_in_dir2 = len(set2)
    files_only_in_dir1 = len(set1 - set2)
    files_only_in_dir2 = len(set2 - set1)
    perfect_matches = len(set1 & set2)

    percent_matched_dir1 = (perfect_matches / files_scanned_in_dir2) * 100
    percent_matched_dir2 = (perfect_matches / files_scanned_in_dir1) * 100

    return (
        files_scanned_in_dir1,
        files_scanned_in_dir2,
        perfect_matches,
        files_only_in_dir1,
        files_only_in_dir2,
        percent_matched_dir1,
        percent_matched_dir2,
        set1,
        set2,
        set_dir1,
        set_dir2
        )


def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Load the UI file
Form, Window = uic.loadUiType("interface.ui")
app = QApplication([])

## MAIN WINDOW CLASS
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Form()
        self.ui.setupUi(self)
        self.check_preferences()
        self.setWindowTitle("BackupInspector")             # set name for window in taskbar and title bar
        self.setWindowIcon(QIcon(resource_path(r"Icons\BackupInspectorIcon.png")))   # add icon to window

        # Left Menu
        self.left_menu_animation = QPropertyAnimation(self.ui.leftMenuContainer, b"maximumWidth")
        self.left_menu_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.left_menu_animation.setDuration(1000)  # Animation duration in milliseconds
        self.ui.leftMenuBtn_UiBtnType.clicked.connect(self.expandorshrink_left_menu)
        self.highlightedLeftMenuBtn = self.ui.homeBtn_UiBtnType
        self.ui.leftMenuContainer.setMaximumWidth(50)   # start with left menu shrunk by setting max width to 50

        self.ui.homeBtn_UiBtnType.clicked.connect(lambda: self.handle_left_menu(page=self.ui.homePage, button=self.ui.homeBtn_UiBtnType))
        self.ui.reportBtn_UiBtnType.clicked.connect(lambda: self.handle_left_menu(page=self.ui.reportPage, button=self.ui.reportBtn_UiBtnType))
        self.ui.dataBtn_UiBtnType.clicked.connect(lambda: self.handle_left_menu(page=self.ui.dataPage, button=self.ui.dataBtn_UiBtnType))
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

        self.init_program()

    def init_program(self):
        
        self.selected_directories1 = []
        self.selected_directories2 = []

        self.list1 = self.ui.list1
        self.list2 = self.ui.list2

        self.ui.pushButton_2_ProgramBtnType.clicked.connect(self.add_folder)
        self.ui.pushButton_3_ProgramBtnType.clicked.connect(self.run_backupinspector)
        self.ui.pushButton_4_ProgramBtnType.clicked.connect(self.add_folder2)
        self.ui.pushButton_5_ProgramBtnType.clicked.connect(self.delete_folder)
        self.ui.pushButton_6_ProgramBtnType.clicked.connect(self.delete_folder2)

        self.ui.show_report_txt_ProgramBtnType.clicked.connect(self.show_results_txt)
        #self.ui.copy_all_missing_files_button_ProgramBtnType.clicked.connect(self.copy_all_missing_files)

        self.ICON_RED_LED = QPixmap(resource_path(r"Icons\LEDs\led-red-on.png"))
        self.ICON_BLUE_LED = QPixmap(resource_path(r"Icons\LEDs\blue-led-on.png"))
        self.ICON_GREEN_LED = QPixmap(resource_path(r"Icons\LEDs\green-led-on.png"))

        self.tiparrow = QPixmap("Icons/arrowtip.png")
        self.notiparrow = QPixmap()



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
        self.ui.dataBtn_UiBtnType.setIcon(self.icon2sw)
        self.ui.reportBtn_UiBtnType.setIcon(self.icon2w)
        self.ui.settingsBtn_UiBtnType.setIcon(self.icon3w)
        self.ui.infoBtn_UiBtnType.setIcon(self.icon4w)
        self.ui.helpBtn_UiBtnType.setIcon(self.icon5w)
        self.ui.centerMenuCloseBtn_UiBtnType.setIcon(self.icon6w)
        self.ui.notificationCloseBtn_UiBtnType.setIcon(self.icon6w)

    def set_icons_black(self):
        self.ui.leftMenuBtn_UiBtnType.setIcon(self.iconb)
        self.ui.homeBtn_UiBtnType.setIcon(self.icon1b)
        self.ui.dataBtn_UiBtnType.setIcon(self.icon2sb)
        self.ui.reportBtn_UiBtnType.setIcon(self.icon2b)
        self.ui.settingsBtn_UiBtnType.setIcon(self.icon3b)
        self.ui.infoBtn_UiBtnType.setIcon(self.icon4b)
        self.ui.helpBtn_UiBtnType.setIcon(self.icon5b)
        self.ui.centerMenuCloseBtn_UiBtnType.setIcon(self.icon6b)
        self.ui.notificationCloseBtn_UiBtnType.setIcon(self.icon6b)

    def check_preferences(self):
        # set the default theme to the one saved in the startup_theme.txt file if it exists otherwqise set it to default
        if os.path.exists("startup_theme.txt"):
            with open("startup_theme.txt", "r") as file:
                self.current_theme = file.read()
                self.ui.themesListSelector.setCurrentText(self.current_theme)     
        else:
            self.current_theme = "default"

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
        # If the center menu is closed (width = 5), then it is opened
        if self.ui.centerMenuContainer.maximumWidth() == 5:
            self.run_animation(self.center_menu_animation, start=5, end=250)
        
        # The correct center menu page is set for centerMenuPagesStack
        self.ui.centerMenuPagesStack.setCurrentWidget(page)

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

        # Save the current theme to the startup_theme.txt file
        with open("startup_theme.txt", "w") as file:
            file.write(self.current_theme)

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



    ### PROGRAM FUNCTIONS ###
    def update_list1(self):
        self.list1.clear()
        for directory in self.selected_directories1:
            item = QListWidgetItem(directory)
            self.list1.addItem(item)
        self.change_run_button_state()
        self.change_user_tip_status_1()

    def update_list2(self):
        self.list2.clear()
        for directory in self.selected_directories2:
            item = QListWidgetItem(directory)
            self.list2.addItem(item)
        self.change_run_button_state()
        self.change_user_tip_status_2()

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
        self.change_user_tip_status_1()

    def delete_folder2(self):
        for item in self.list2.selectedItems():
            self.selected_directories2.remove(item.text())
            self.list2.takeItem(self.list2.row(item))
        self.change_run_button_state()
        self.change_user_tip_status_2()
    

    def change_user_tip_status_1(self):
        if self.selected_directories1:
            # move the QtextBrowser to the back layer
            self.ui.ref_user_tip.lower()
            # remove arrow from label pixmap by setting to no pixmap
            #self.ui.tip_arrow_1.setPixmap(self.notiparrow)
        else:
            # move the QtextBrowser to the front layer
            self.ui.ref_user_tip.raise_()
            # add arrow to label pixmap
            #self.ui.tip_arrow_1.setPixmap(self.tiparrow)

    def change_user_tip_status_2(self):
        if self.selected_directories2:
            # move the QtextBrowser to the back layer
            self.ui.target_user_tip.lower()
            # remove arrow from label pixmap
            #self.ui.tip_arrow_2.setPixmap(self.notiparrow)
        else:
            # move the QtextBrowser to the front layer
            self.ui.target_user_tip.raise_()
            # add arrow to label pixmap
            #self.ui.tip_arrow_2.setPixmap(self.tiparrow)

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
        self.ui.show_report_txt_ProgramBtnType.setEnabled(True)

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
            for file in self.set1 - self.set2:
                f.write(f"\n# {file}\n")
            """
            # Write list of the file names of the files that are only in dir2
            f.write("\nFiles only in dir2:\n")
            for file in set2 - set1:
                f.write(f"\n# {file}\n")
            """

        # Open the file in Notepad 
        subprocess.Popen(["notepad.exe", file_path])   # Subprocess so as not to block the rest of the program



    # function to copy all missing files to target
    def copy_all_missing_files(self):
        missing_files = self.set1 - self.set2

        # find the corresponding file in set_dir1
        for file in missing_files:
            for file_path in self.set_dir1:
                if file == os.path.basename(file_path):
                    # find the corresponding target directory by checking if the file_path contains any of the the selected directoies in self.selected_directories2
                    for target_dir in self.selected_directories2:
                        if target_dir in file_path:
                            # copy file to target directory
                            shutil.copy(file_path, target_dir)
                            print(f"{file_path} copied to {target_dir}")
                            break  
                        else:
                            print(f"Could not find target directory {target_dir} for {file_path}")

    def change_run_button_state(self):
        if self.selected_directories1 and self.selected_directories2:
            self.ui.pushButton_3_ProgramBtnType.setEnabled(True)
        else:
            self.ui.pushButton_3_ProgramBtnType.setEnabled(False)


    def run_backupinspector(self):
        reference_dirs = self.selected_directories1
        target_dirs = self.selected_directories2
        self.files_scanned_1, self.files_scanned_2, self.num_perfect_matches, self.num_files_only_in_dir1, self.num_files_only_in_dir2, self.percent_matched_dir1, self.percent_matched_dir2, self.set1, self.set2, self.set_dir1, self.set_dir2 = compare_directories(reference_dirs, target_dirs)
        
        self.update_led()
        self.update_results()



if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



