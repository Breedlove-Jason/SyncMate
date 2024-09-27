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
            150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
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

        # Add grid layout to main layout
        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

        # Load external stylesheet
        self.load_stylesheet()

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle("SyncMate Rsync Tool")

    def browse_source(self):
        if self.source_type.currentText() == "Directory":
            dir_name = QFileDialog.getExistingDirectory(self, "Select Source Directory")
            if dir_name:
                self.source_input.setText(dir_name)
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Source File")
            if file_name:
                self.source_input.setText(file_name)

    def browse_dest(self):
        if self.dest_type.currentText() == "Directory":
            dir_name = QFileDialog.getExistingDirectory(
                self, "Select Destination Directory"
            )
            if dir_name:
                self.dest_input.setText(dir_name)
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Destination File")
            if file_name:
                self.dest_input.setText(file_name)

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
