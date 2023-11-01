
from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QApplication, QMainWindow
import pyi_splash

# Close the splash screen. It does not matter when the call
# to this function is made, the splash screen remains open until
# this function is called or the Python program is terminated.
pyi_splash.close()

#%% - Backend 
import os
import datetime
import subprocess

def count_subdirectories(directory):
    subdirectories_count = 0

    for entry in os.scandir(directory):
        if entry.is_dir():
            subdirectories_count += 1

    return subdirectories_count

def file_generator(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield file

def compare_directories(reference_dirs, target_dirs, return_lost_file_list=False):
    set1 = set()
    set2 = set()

    for dir1 in reference_dirs:
        gen1 = file_generator(dir1)
        for file1 in gen1:
            set1.add(file1)

    for dir2 in target_dirs:
        gen2 = file_generator(dir2)
        for file2 in gen2:
            set2.add(file2)

    files_scanned_in_dir1 = len(set1)
    files_scanned_in_dir2 = len(set2)
    perfect_matches = len(set1 & set2)
    files_only_in_dir1 = len(set1 - set2)
    files_only_in_dir2 = len(set2 - set1)

    percent_matched_dir1 = (perfect_matches / files_scanned_in_dir2) * 100
    percent_matched_dir2 = (perfect_matches / files_scanned_in_dir1) * 100

    if return_lost_file_list:

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

        with open(file_path, "w") as f:
            # Write the title of the file as BACKUPINSPECTOR RESULTS
            f.write("BACKUPINSPECTOR RESULTS\n")

            # Add the date and time of the scan
            f.write(f"Scan date: {datetime.datetime.now()}\n")

            # Write the number of files scanned in total for the refrence dirs (dir1)
            f.write(f"\nFiles scanned in refrence dirs: {files_scanned_in_dir1}\n")

            # Write the number of files scanned in total for the target dirs (dir2)
            f.write(f"Files scanned in target dirs: {files_scanned_in_dir2}\n")

            # Write the number of perfect matches
            f.write(f"Number of perfect matches: {perfect_matches}\n")

            # Write number of files in refrence dirs (dir1) that are not in target dirs (dir2)
            f.write(f"Files in reference not in target: {files_only_in_dir1}\n")

            # Write number of files in target dirs (dir2) that are not in refrence dirs (dir1)
            f.write(f"Files in target not in reference: {files_only_in_dir2}\n\n\n")


            # Write list of the file names of the files that are only in dir1
            f.write("\n### Files missing from Target:\n")
            for file in set1 - set2:
                f.write(f"\n# {file}\n")
            """
            # Write list of the file names of the files that are only in dir2
            f.write("\nFiles only in dir2:\n")
            for file in set2 - set1:
                f.write(f"\n# {file}\n")
            """

    # Open the file in Notepad 
    subprocess.Popen(["notepad.exe", file_path])   # Subprocess so as not to block the rest of the program

    return (
        files_scanned_in_dir1,
        files_scanned_in_dir2,
        perfect_matches,
        files_only_in_dir1,
        files_only_in_dir2,
        percent_matched_dir1,
        percent_matched_dir2,
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

        self.form.pushButton.clicked.connect(self.edit_folder)
        self.form.pushButton_2.clicked.connect(self.add_folder)
        self.form.pushButton_3.clicked.connect(self.run_backupinspector)
        self.form.pushButton_4.clicked.connect(self.add_folder2)
        self.form.pushButton_5.clicked.connect(self.delete_folder)
        self.form.pushButton_6.clicked.connect(self.delete_folder2)
        self.form.pushButton_7.clicked.connect(self.edit_folder2)
        self.show()
            
    def update_list1(self):
        self.list1.clear()
        for directory in self.selected_directories1:
            item = QListWidgetItem(directory)
            self.list1.addItem(item)

    def update_list2(self):
        self.list2.clear()
        for directory in self.selected_directories2:
            item = QListWidgetItem(directory)
            self.list2.addItem(item)


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

    def delete_folder2(self):
        for item in self.list2.selectedItems():
            self.selected_directories2.remove(item.text())
            self.list2.takeItem(self.list2.row(item))

    def edit_folder(self):
        #print("Edit Folder1")
        pass
    def edit_folder2(self):
        #print("Edit Folder2")
        pass
    def run_backupinspector(self):
        reference_dirs = self.selected_directories1
        target_dirs = self.selected_directories2
        files_scanned_1, files_scanned_2, num_perfect_matches, num_files_only_in_dir1, num_files_only_in_dir2, percent_matched_dir1, percent_matched_dir2 = compare_directories(reference_dirs, target_dirs, return_lost_file_list=True)


window = MainWindow()
app.exec()

