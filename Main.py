
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


#%% - GUI


Form, Window = uic.loadUiType("BackupInspector_GUI.ui")
app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.form = Form()
        self.form.setupUi(self)

        self.selected_directories1 = []
        self.selected_directories2 = []

        self.list1 = self.form.list1
        self.list2 = self.form.list2

        self.form.pushButton_2.clicked.connect(self.add_folder)
        self.form.pushButton_3.clicked.connect(self.run_backupinspector)
        self.form.pushButton_4.clicked.connect(self.add_folder2)
        self.form.pushButton_5.clicked.connect(self.delete_folder)
        self.form.pushButton_6.clicked.connect(self.delete_folder2)

        self.form.show_report_txt.clicked.connect(self.show_results_txt)
        #self.form.copy_all_missing_files_button.clicked.connect(self.copy_all_missing_files)

        self.ICON_RED_LED = QPixmap("Icons/led-red-on.png")
        self.ICON_BLUE_LED = QPixmap("Icons/led-blue-on.png")
        self.ICON_GREEN_LED = QPixmap("Icons/green-led-on.png")

        self.tiparrow = QPixmap("Icons/arrowtip.png")
        self.notiparrow = QPixmap()
        
        self.show()
            
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
            self.form.ref_user_tip.lower()
            # remove arrow from label pixmap by setting to no pixmap
            self.form.tip_arrow_1.setPixmap(self.notiparrow)
        else:
            # move the QtextBrowser to the front layer
            self.form.ref_user_tip.raise_()
            # add arrow to label pixmap
            self.form.tip_arrow_1.setPixmap(self.tiparrow)

    def change_user_tip_status_2(self):
        if self.selected_directories2:
            # move the QtextBrowser to the back layer
            self.form.target_user_tip.lower()
            # remove arrow from label pixmap
            self.form.tip_arrow_2.setPixmap(self.notiparrow)
        else:
            # move the QtextBrowser to the front layer
            self.form.target_user_tip.raise_()
            # add arrow to label pixmap
            self.form.tip_arrow_2.setPixmap(self.tiparrow)

    # function to toggle led's state based on results
    def update_led(self):
        number = self.files_scanned_1 - self.num_perfect_matches
        if number == 0:
            self.form.feedback_led.setPixmap(self.ICON_GREEN_LED)
        else:
            self.form.feedback_led.setPixmap(self.ICON_RED_LED)

    def update_results(self):
        # update a qlcdnumber widgets with the number of files scanned
        self.form.scanned_files_readoutcount.display(self.files_scanned_1)
        self.form.missing_files_readoutcount.display(self.files_scanned_1 - self.num_perfect_matches)

        if self.files_scanned_1 - self.num_perfect_matches == 0:
            self.form.test_status_text.setText("TEST: PASSED")
        else:
            self.form.test_status_text.setText("TEST: FAILED")


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
            self.form.pushButton_3.setEnabled(True)
        else:
            self.form.pushButton_3.setEnabled(False)


    def run_backupinspector(self):
        reference_dirs = self.selected_directories1
        target_dirs = self.selected_directories2
        self.files_scanned_1, self.files_scanned_2, self.num_perfect_matches, self.num_files_only_in_dir1, self.num_files_only_in_dir2, self.percent_matched_dir1, self.percent_matched_dir2, self.set1, self.set2, self.set_dir1, self.set_dir2 = compare_directories(reference_dirs, target_dirs)
        
        self.update_led()
        self.update_results()




window = MainWindow()
app.exec()

