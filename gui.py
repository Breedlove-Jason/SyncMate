import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QGridLayout,
    QMessageBox,
    QSizePolicy,
    QCheckBox,
)


class SyncMateGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Logo (with reduced size)
        self.logo_label = QLabel(self)
        logo_path = os.path.join(
            os.path.dirname(__file__), "resources", "syncmate_logo.jpeg"
        )
        self.logo_pixmap = QPixmap(logo_path)
        self.logo_pixmap = self.logo_pixmap.scaled(
            150, 150, Qt.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)

        # Title Label
        self.title_label = QLabel("SyncMate Rsync Tool", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title_label")  # For styling

        # Inputs
        self.source_input = QLineEdit(self)
        self.source_input.setPlaceholderText("Source")
        self.source_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.dest_input = QLineEdit(self)
        self.dest_input.setPlaceholderText("Destination")
        self.dest_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Rsync options
        self.dry_run_checkbox = QCheckBox("--dry-run", self)
        self.dry_run_checkbox.setObjectName("top_checkbox")
        self.delete_checkbox = QCheckBox("--delete", self)
        self.delete_checkbox.setObjectName("top_checkbox")
        self.compress_checkbox = QCheckBox("--compress", self)
        self.compress_checkbox.setObjectName("top_checkbox")
        self.verbose_checkbox = QCheckBox("--verbose", self)
        self.verbose_checkbox.setObjectName("top_checkbox")

        # Exclude patterns
        self.exclude_label = QLabel("Exclude Patterns (comma-separated):", self)
        self.exclude_label.setObjectName("exclude_label")
        self.exclude_input = QLineEdit(self)
        self.exclude_input.setObjectName("exclude_input")
        self.exclude_input.setPlaceholderText("Exclude patterns")

        # File/Directory selection type dropdown
        self.source_type = QComboBox(self)
        self.source_type.addItems(["Directory", "File"])

        self.dest_type = QComboBox(self)
        self.dest_type.addItems(["Directory", "File"])

        # Buttons
        self.source_browse_btn = QPushButton("Browse", self)
        self.source_browse_btn.setIcon(
            QIcon("resources/folder-open.svg")
        )  # Placeholder

        self.dest_browse_btn = QPushButton("Browse", self)
        self.dest_browse_btn.setIcon(QIcon("resources/folder-open.svg"))  # Placeholder

        # Connect browse buttons to the browse methods
        self.source_browse_btn.clicked.connect(self.browse_source)
        self.dest_browse_btn.clicked.connect(self.browse_dest)

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.logo_label)

        # Create a grid layout for inputs
        grid_layout = QGridLayout()

        # Title Layout
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        title_layout.setAlignment(Qt.AlignCenter)

        # Add title_layout to the grid layout at row 0, spanning 3 columns
        grid_layout.addLayout(title_layout, 0, 0, 1, 3)

        # Source row (row 1)
        grid_layout.addWidget(self.source_input, 1, 0)
        grid_layout.addWidget(self.source_type, 1, 1)
        grid_layout.addWidget(self.source_browse_btn, 1, 2)

        # Destination row (row 2)
        grid_layout.addWidget(self.dest_input, 2, 0)
        grid_layout.addWidget(self.dest_type, 2, 1)
        grid_layout.addWidget(self.dest_browse_btn, 2, 2)

        # Set column stretch to make input fields expand
        grid_layout.setColumnStretch(0, 1)  # Input field column
        grid_layout.setColumnStretch(1, 0)  # Type dropdown column
        grid_layout.setColumnStretch(2, 0)  # Browse button column

        # Options layout
        options_layout = QGridLayout()

        # Create a horizontal layout for the top checkboxes
        top_checkboxes_layout = QHBoxLayout()
        top_checkboxes_layout.addWidget(self.dry_run_checkbox)
        top_checkboxes_layout.addWidget(self.delete_checkbox)
        top_checkboxes_layout.addWidget(self.compress_checkbox)
        top_checkboxes_layout.addWidget(self.verbose_checkbox)
        top_checkboxes_layout.setAlignment(Qt.AlignCenter)

        # Add the top checkboxes layout to the options layout
        options_layout.addLayout(top_checkboxes_layout, 0, 0, 1, 2, Qt.AlignCenter)

        # Exclude pattern widgets
        options_layout.addWidget(self.exclude_label, 1, 0, 1, 2, Qt.AlignCenter)
        options_layout.addWidget(self.exclude_input, 2, 0, 1, 2, Qt.AlignCenter)

        # Add options layout to main layout
        grid_layout.addLayout(options_layout, 3, 0, 1, 3)

        # Add grid layout to main layout
        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

        # Load external stylesheet
        self.load_stylesheet()

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle("SyncMate Rsync Tool")

    def browse_source(self):
        """
        This method opens a file dialog to allow the user to select a source, either a directory or a file.
        Based on the user's choice from a combo box, it will open the appropriate dialog type.
        If the user selects a directory or file, the path is set to a text input field.

        :return: None
        """
        if self.source_type.currentText() == "Directory":
            dir_name = QFileDialog.getExistingDirectory(self, "Select Source Directory")
            if dir_name:
                self.source_input.setText(dir_name)
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Source File")
            if file_name:
                self.source_input.setText(file_name)

    def browse_dest(self):
        """
        Opens a file or directory dialog depending on the selected destination type
        and updates the destination input field with the selected path.

        :return: None
        """
        if self.dest_type.currentText() == "Directory":
            dir_name = QFileDialog.getExistingDirectory(
                self, "Select Destination Directory"
            )
            if dir_name:
                self.dest_input.setText(dir_name)
        else:
            file_name, _ = QFileDialog.getSaveFileName(self, "Select Destination File")
            if file_name:
                self.dest_input.setText(file_name)

    def validate_paths(self):
        """
        Validates the selected source and destination paths.

        Checks if the source and destination paths are provided and verifies
        the existence of the specified source path based on the selected source type
        (either Directory or File).

        :return:
            - True if both paths are valid and the source path exists.
            - False otherwise and displays an appropriate warning message.
        """
        source = self.source_input.text()
        dest = self.dest_input.text()

        if not source or not dest:
            QMessageBox.warning(
                self, "Warning", "Please select both a source and destination path."
            )
            return False
        if self.source_type.currentText() == "Directory" and not os.path.isdir(source):
            QMessageBox.warning(self, "Warning", "Source path does not exist.")
            return False
        if self.source_type.currentText() == "File" and not os.path.isfile(source):
            QMessageBox.warning(self, "Warning", "Source file does not exist.")
            return False
        return True

    def load_stylesheet(self):
        # Load stylesheet from external .qss file
        qss_path = os.path.join(os.path.dirname(__file__), "resources", "styles.qss")
        with open(qss_path, "r") as file:
            self.setStyleSheet(file.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SyncMateGUI()
    ex.show()
    sys.exit(app.exec())
