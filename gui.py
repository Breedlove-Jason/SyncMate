from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QApplication,
    QComboBox,
)
import sys


class SyncMateGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Inputs
        self.dest_input = QLineEdit(self)
        self.source_input = QLineEdit(self)

        # Labels
        self.dest_label = QLabel("Destination", self)
        self.source_label = QLabel("Source", self)

        # File/Directory selection type dropdown
        self.source_type = QComboBox(self)
        self.source_type.addItems(["Directory", "File"])

        self.dest_type = QComboBox(self)
        self.dest_type.addItems(["Directory", "File"])

        # Buttons
        self.source_browse_btn = QPushButton("Browse", self)
        self.dest_browse_btn = QPushButton("Browse", self)

        # Connect browse buttons to the browse methods
        self.source_browse_btn.clicked.connect(self.browse_source)
        self.dest_browse_btn.clicked.connect(self.browse_dest)

        # Set up the layout
        layout = QVBoxLayout()

        # Add widgets to the layout
        layout.addWidget(self.source_label)
        layout.addWidget(self.source_input)
        layout.addWidget(self.source_type)  # Add the file/directory dropdown
        layout.addWidget(self.source_browse_btn)

        layout.addWidget(self.dest_label)
        layout.addWidget(self.dest_input)
        layout.addWidget(self.dest_type)  # Add the file/directory dropdown
        layout.addWidget(self.dest_browse_btn)

        self.setLayout(layout)
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle("SyncMate Rsync Tool")

    def browse_source(self):
        print("Opening source directory dialog...")  # Debugging log
        if self.source_type.currentText() == "Directory":
            # Browse for directory
            dir_name = QFileDialog.getExistingDirectory(self, "Select Source Directory")
            if dir_name:
                self.source_input.setText(dir_name)
                print(f"Source directory selected: {dir_name}")  # Debugging log
            else:
                print("No source directory selected.")  # Debugging log
        else:
            # Browse for file
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Source File")
            if file_name:
                self.source_input.setText(file_name)
                print(f"Source file selected: {file_name}")  # Debugging log
            else:
                print("No source file selected.")  # Debugging log

    def browse_dest(self):
        print("Opening destination directory dialog...")  # Debugging log
        if self.dest_type.currentText() == "Directory":
            # Browse for directory
            dir_name = QFileDialog.getExistingDirectory(
                self, "Select Destination Directory"
            )
            if dir_name:
                self.dest_input.setText(dir_name)
                print(f"Destination directory selected: {dir_name}")  # Debugging log
            else:
                print("No destination directory selected.")  # Debugging log
        else:
            # Browse for file
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Destination File")
            if file_name:
                self.dest_input.setText(file_name)
                print(f"Destination file selected: {file_name}")  # Debugging log
            else:
                print("No destination file selected.")  # Debugging log


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SyncMateGUI()

    # Show the window
    ex.show()

    sys.exit(app.exec())
