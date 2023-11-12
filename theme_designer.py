import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QColorDialog, QFormLayout, QFileDialog
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi
import resources_rc
import re
import os


class ThemeCustomiser(QWidget):
    def __init__(self, ui_file_path):
        super().__init__()

        #  set  default window size
        self.resize(1000, 800)

        self.ui_file_path = ui_file_path
        self.ui_preview = loadUi(self.ui_file_path)
        self.ui_preview.setObjectName('previewMainWindow')
        self.ui_preview.uiThemeBtn_UiBtnType.clicked.connect(self.toggle_edit_mode)

        self.color_pick_buttons = {}

        self.init_css_theme()
        self.edit_mode = "dark"
        self.init_theme_customiser_ui()


    def init_css_theme(self):
        # load default dark theme into the string
        with open('themes/default/dark_mode.css', 'r') as file:
            self.dark_mode_css_content = file.read()

        # load default light theme into the string
        with open('themes/default/light_mode.css', 'r') as file:
            self.light_mode_css_content = file.read()

        self.theme_groups = ["Main",
                                "Accent_1",
                                "Accent_2",
                                "Accent_3",
                                "Text_1",
                                "Text_2"]  
        
        self.dark_mode_colors = ["#16191d",
                                "#1f232a",
                                "#2c313c",
                                "#343b47",
                                "#fff",
                                "#838ea2"]  
        
        self.light_mode_colors = ["#ffffff",
                                "#e4e7ec",
                                "#c5ccd9",
                                "#b2bac8",
                                "#16191d",
                                "#2c313c"]

        # initialise the color mapping dictionary
        self.color_mapping = {}

    def toggle_edit_mode(self):
        if self.edit_mode == "dark":
            self.edit_mode = "light"
            self.ui_preview.setStyleSheet(self.light_mode_css_content)
            
        else:
            self.edit_mode = "dark"
            self.ui_preview.setStyleSheet(self.dark_mode_css_content)
            

    def init_theme_customiser_ui(self):
        self.setWindowTitle('Theme Customiser')

        preview_label = QLabel('Preview:')
        edit_layout = QFormLayout()

        for obj_name, obj_colour in zip(self.theme_groups, self.dark_mode_colors):
            color_picker_button = QPushButton(f'Edit {obj_name} Color ({obj_colour})')
            color_picker_button.setObjectName(obj_name)
            color_picker_button.clicked.connect(self.color_picker)
            edit_layout.addRow(obj_name, color_picker_button)
            self.color_pick_buttons[obj_name] = color_picker_button

        save_button = QPushButton('Save Theme')
        save_button.clicked.connect(self.save_theme)
        edit_layout.addRow(save_button)

        layout = QVBoxLayout()
        layout.addWidget(preview_label, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.ui_preview)
        layout.addLayout(edit_layout)
        self.setLayout(layout)

    def save_theme(self):
        ### FIIIX THIS !!!!!!!!!!!!

        # create a simple ui popup that has a text box and asks user to type the title for the theme into the box 
        theme_name, _ = QFileDialog.getSaveFileName(self, 'Save Theme', 'themes', 'CSS Files (*.css)')
        theme_name = theme_name.split('/')[-1].split('.')[0]

        # create a new folder in the themes folder with the name of the theme
        os.mkdir(f'themes/{theme_name}')

        # save the dark mode css file to the new folder
        with open(f'themes/{theme_name}/dark_mode.css', 'w') as file:
            file.write(self.dark_mode_css_content)
        
        # save the light mode css file to the new folder
        with open(f'themes/{theme_name}/light_mode.css', 'w') as file:
            file.write(self.light_mode_css_content)

        
    def color_picker(self):
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle('Choose Color')

        sender_name = self.sender().objectName()
        initial_color = QColor(self.ui_preview.palette().color(QPalette.ColorRole.Window))

        if initial_color.isValid():
            color_dialog.setCurrentColor(initial_color)

        if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
            color = color_dialog.selectedColor()

        if self.edit_mode == "dark":
            self.dark_mode_colors, self.dark_mode_css_content = self.create_color_mapping(sender_name, color, self.dark_mode_colors, self.dark_mode_css_content)
            self.update_ui_preview(self.dark_mode_css_content)
        else:
            self.light_mode_colors, self.light_mode_css_content = self.create_color_mapping(sender_name, color, self.light_mode_colors, self.light_mode_css_content)
            self.update_ui_preview(self.light_mode_css_content)

    def create_color_mapping(self, object_name, color, mode_colors, mode_css):
        # find the correpsonding colour in the theme_groups to the object_name and print it
        for obj_name, obj_color in zip(self.theme_groups, mode_colors):
            if obj_name == object_name:
                original_color = obj_color

        print(f'Updating {object_name} from {original_color}  to {color.name()}')

        # Create a mapping of the original color to the new color
        self.color_mapping[original_color] = color.name()

        # update the theme_colors list with the new color
        for i, obj_name in enumerate(self.theme_groups):
            if obj_name == object_name:
                mode_colors[i] = color.name()

        # update the color of the button
        self.color_pick_buttons[object_name].setStyleSheet(f'background-color: {color.name()};')

        # Define a regex pattern for color patterns
        color_pattern = re.compile(r'#([a-fA-F\d]{3,6}|[a-fA-F\d]{8})|rgb\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*\)|hsl\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*\)')

        # Find all color matches in the CSS content
        color_matches = color_pattern.finditer(mode_css)

        # Store color positions and values in a list
        color_positions = []
        for match in color_matches:
            color_positions.append((match.start(), match.end()))
        
        # Update colors based on the provided mapping
        for start, end in color_positions:
            original_color = mode_css[start:end]
            new_color = self.color_mapping.get(original_color, original_color)
            mode_css = mode_css[:start] + new_color + mode_css[end:]
        
        return mode_colors, mode_css

    def update_ui_preview(self, css_content):
        self.ui_preview.setStyleSheet(css_content)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Replace 'your_ui_file.ui' with the actual path to your UI file
    ui_file_path = 'interface.ui'

    customizer = ThemeCustomiser(ui_file_path)
    customizer.show()

    sys.exit(app.exec())
