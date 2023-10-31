
from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QApplication, QMainWindow

from BackupInspector_Backend import compare_directories
import pyi_splash

# Close the splash screen. It does not matter when the call
# to this function is made, the splash screen remains open until
# this function is called or the Python program is terminated.
pyi_splash.close()




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
        print("Edit Folder1")

    def edit_folder2(self):
        print("Edit Folder2")

    def run_backupinspector(self):
        reference_dirs = self.selected_directories1
        target_dirs = self.selected_directories2
        files_scanned_1, files_scanned_2, num_perfect_matches, num_files_only_in_dir1, num_files_only_in_dir2, percent_matched_dir1, percent_matched_dir2 = compare_directories(reference_dirs, target_dirs, return_lost_file_list=True)


window = MainWindow()
app.exec()

