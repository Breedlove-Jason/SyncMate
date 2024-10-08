import os
import sys
import shutil
import json
import threading
import time
import schedule
from PySide6.QtCore import Qt, QSize, QDateTime
from PySide6.QtGui import QIcon, QPixmap, QFontDatabase, QFont
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
    QDialog,
    QTextEdit,
    QProgressBar,
    QSpinBox,
    QInputDialog,
    QSystemTrayIcon,
    QListWidget,
    QDateTimeEdit,
)


from rsync_manager import RsyncThread


class SyncMateGUI(QWidget):
    """
    SyncMateGUI class represents the graphical user interface for a Rsync tool application.
    It provides various input fields, options, and buttons to configure and start Rsync synchronization tasks.

    Methods
    -------
    __init__():
        Initializes the GUI, including setting up directories, loading fonts and resources,
        and arranging all interactive widgets.

    load_profiles():
        Loads the available profiles from the "profiles" directory and populates the profile dropdown menu.
    """

    def __init__(self):
        super().__init__()

        # Add profiles directory, if it doesn't exist then create it
        self.profiles_dir = os.path.join(os.path.dirname(__file__), "profiles")
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
        
        # Scheduler thread
        self.scheduled_tasks = []
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()

        self.load_scheduled_tasks()


        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                self, "Systray", "No system tray available on this system."
            )
            sys.exit(1)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("resources/sync.svg"))
        self.tray_icon.show()



        # Load custom font
        self.cancel_button = None
        self.progress_bar = None
        self.output_text = None
        self.output_dialog = None
        self.rsync_thread = None
        source_sans_reg_path = os.path.join(
            os.path.dirname(__file__), "resources", "SourceSansPro-Regular.otf"
        )
        QFontDatabase.addApplicationFont(source_sans_reg_path)
        self.setFont(QFont("Source Sans Pro", 16))

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
        self.source_input.setObjectName("source_input")

        self.dest_input = QLineEdit(self)
        self.dest_input.setPlaceholderText("Destination")
        self.dest_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dest_input.setObjectName("dest_input")

        # Rsync options
        self.dry_run_checkbox = QCheckBox("--dry-run", self)
        self.dry_run_checkbox.setObjectName("dry_run_checkbox")
        self.delete_checkbox = QCheckBox("--delete", self)
        self.delete_checkbox.setObjectName("delete_checkbox")
        self.compress_checkbox = QCheckBox("--compress", self)
        self.compress_checkbox.setObjectName("compress_checkbox")
        self.verbose_checkbox = QCheckBox("--verbose", self)
        self.verbose_checkbox.setObjectName("verbose_checkbox")

        # Exclude patterns
        self.exclude_label = QLabel("Exclude Patterns (comma-separated):", self)
        self.exclude_label.setObjectName("exclude_label")
        self.exclude_input = QLineEdit(self)
        self.exclude_input.setObjectName("exclude_input")
        self.exclude_input.setPlaceholderText("Exclude patterns")

        # Profiles
        self.profile_label = QLabel("Profiles:", self)
        self.profile_label.setObjectName("profile_label")

        self.profile_combo = QComboBox(self)
        self.profile_combo.setObjectName("profile_combo")
        self.load_profiles()

        self.save_profile_btn = QPushButton("Save Profile", self)
        self.save_profile_btn.setObjectName("save_profile_btn")
        self.save_profile_btn.clicked.connect(self.save_profile)

        self.delete_profile_btn = QPushButton("Delete Profile", self)
        self.delete_profile_btn.setObjectName("delete_profile_btn")
        self.delete_profile_btn.clicked.connect(self.delete_profile)

        self.load_profile_btn = QPushButton("Load Profile", self)
        self.load_profile_btn.setObjectName("load_profile_btn")
        self.load_profile_btn.clicked.connect(self.load_profile)

        # Schedule button
        self.schedule_button = QPushButton("Schedule Sync", self)
        self.schedule_button.setObjectName("schedule_button")
        self.schedule_button.clicked.connect(self.open_schedule_dialog)

        # Schedule Tasks List
        self.tasks_label = QLabel("Scheduled Tasks", self)
        self.tasks_label.setObjectName("tasks_label")

        self.tasks_list = QListWidget(self)
        self.tasks_list.setObjectName("tasks_list")

        # Bandwidth limit
        self.bwlimit_label = QLabel("Bandwidth Limit (KB/s):", self)
        self.bwlimit_label.setObjectName("bwlimit_label")

        self.bwlimit_input = QSpinBox(self)
        self.bwlimit_input.setRange(0, 999999)
        self.bwlimit_input.setSuffix(" KB/s")
        self.bwlimit_input.setObjectName("bwlimit_input")
        self.bwlimit_input.setValue(0)

        # File/Directory selection type dropdown
        self.source_type = QComboBox(self)
        self.source_type.addItems(["Directory", "File"])
        self.source_type.setObjectName("source_type")

        self.dest_type = QComboBox(self)
        self.dest_type.addItems(["Directory", "File"])
        self.dest_type.setObjectName("dest_type")

        # Buttons
        self.sync_button = QPushButton("Start Sync", self)
        self.sync_button.setObjectName("sync_button")
        # self.sync_button.setIcon(QIcon("resources/sync.svg"))  # Set sync.svg icon
        # Set sync.svg icon with specified size
        self.sync_button.setIcon(QIcon("resources/sync.svg"))
        self.sync_button.setIconSize(QSize(30, 30))
        self.sync_button.clicked.connect(self.start_sync)

        self.source_browse_btn = QPushButton("Browse", self)
        self.source_browse_btn.setIcon(
            QIcon("resources/folder-open.svg")
        )  # Placeholder
        self.source_browse_btn.setObjectName("source_browse_btn")

        self.dest_browse_btn = QPushButton("Browse", self)
        self.dest_browse_btn.setIcon(QIcon("resources/folder-open.svg"))  # Placeholder
        self.dest_browse_btn.setObjectName("dest_browse_btn")

        # Connect browse buttons to the browse methods
        self.source_browse_btn.clicked.connect(self.browse_source)
        self.dest_browse_btn.clicked.connect(self.browse_dest)

        # Set up the main layout
        main_layout = QVBoxLayout()
        # main_layout.addWidget(self.logo_label)

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

        # Profile Layout
        profiles_layout = QHBoxLayout()
        profiles_layout.addWidget(self.profile_label)
        profiles_layout.addWidget(self.profile_combo)
        profiles_layout.addWidget(self.load_profile_btn)
        profiles_layout.addWidget(self.save_profile_btn)
        profiles_layout.addWidget(self.delete_profile_btn)

        # Add profiles_layout to main layout
        main_layout.addLayout(profiles_layout)
        # Add logo to main layout
        main_layout.addWidget(self.logo_label)
        # Add Schedule button to main layout
        main_layout.addWidget(self.schedule_button, alignment=Qt.AlignCenter)
        # Add Scheduled tasks list to main layout
        main_layout.addWidget(self.tasks_label)
        main_layout.addWidget(self.tasks_list)

        # Add the top checkboxes layout to the options layout
        options_layout.addLayout(top_checkboxes_layout, 0, 0, 1, 2, Qt.AlignCenter)

        # Exclude pattern widgets
        options_layout.addWidget(self.exclude_label, 1, 0, 1, 2, Qt.AlignCenter)
        options_layout.addWidget(self.exclude_input, 2, 0, 1, 2, Qt.AlignCenter)

        # Bandwidth limit widgets
        options_layout.addWidget(self.bwlimit_label, 3, 0, 1, 1, Qt.AlignRight)
        options_layout.addWidget(self.bwlimit_input, 3, 1, 1, 1, Qt.AlignLeft)

        # Add options layout to main layout
        grid_layout.addLayout(options_layout, 3, 0, 1, 3)

        # Add grid layout to main layout
        main_layout.addWidget(self.sync_button, alignment=Qt.AlignCenter)

        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

        # Load external stylesheet
        self.load_stylesheet()

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle("SyncMate Rsync Tool")



    def run_scheduler(self):
        """
        Continuously runs the scheduled tasks.
        """
        while True:
            schedule.run_pending()
            time.sleep(1)


    def save_scheduled_tasks(self):
        """
        Saves the scheduled tasks to a JSON file.
        """
        tasks_file = os.path.join(self.profiles_dir, "scheduled_tasks.json")
        with open(tasks_file, "w") as file:
            json.dump(self.scheduled_tasks, file, default=str)

    def load_scheduled_tasks(self):
        """
        Loads the scheduled tasks from a JSON file.
        """
        tasks_file = os.path.join(self.profiles_dir, "scheduled_tasks.json")
        if os.path.exists(tasks_file):
            with open(tasks_file, "r") as file:
                self.scheduled_tasks = json.load(file)
                for task in self.scheduled_tasks:
                    run_time = QDateTime.fromString(task['time'], Qt.ISODate).toPyDateTime()
                    schedule.every().day.at(run_time.strftime('%H:%M:%S')).do(self.execute_scheduled_task, task['profile']).tag(task['name'])
                    self.tasks_list.addItem(task['name'])

    def open_schedule_dialog(self):
        """
        Opens a dialog to schedule a sync task.

        This method creates a dialog window with a date and time picker, allowing the user to schedule a sync task.
        The selected date and time are passed to the `schedule_task` method when the "Schedule" button is clicked.

        :return: None
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Schedule Sync")
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        datetime_label = QLabel("Select Date and Time:", dialog)
        datetime_edit = QDateTimeEdit(dialog)
        datetime_edit.setCalendarPopup(True)
        datetime_edit.setDateTime(QDateTime.currentDateTime())

        schedule_btn = QPushButton("Schedule", dialog)
        schedule_btn.clicked.connect(
            lambda: self.schedule_task(dialog, datetime_edit.dateTime())
        )

        layout.addWidget(datetime_label)
        layout.addWidget(datetime_edit)
        layout.addWidget(schedule_btn)

        dialog.exec()


    def schedule_task(self, dialog, datetime):
        dialog.accept()
        run_time = datetime.toPython()
        profile_data = self.get_current_settings()
        profile_name = f"Scheduled Task - {run_time.strftime('%Y-%m-%d %H:%M:%S')}"

        # Save the task details
        scheduled_task = {
            'time':run_time,
            'profile':profile_data,
            'name':profile_name
        }
        self.scheduled_tasks.append(scheduled_task)
        self.tasks_list.addItem(profile_name)

        # Schedule the task
        schedule_time_str = run_time.strftime('%Y-%m-%d %H:%M:%S')
        schedule.every().day.at(run_time.strftime('%H:%M:%S')).do(self.execute_scheduled_task, profile_data).tag(profile_name)
        QMessageBox.information(self, "Task Scheduled", f"Sync scheduled for {schedule_time_str}.")

        # Save the scheduled tasks to a file
        self.save_scheduled_tasks()

    def get_current_settings(self):
        return {
            'source': self.source_input.text(),
            'destination': self.dest_input.text(),
            'source_type': self.source_type.currentText(),
            'dest_type': self.dest_type.currentText(),
            'dry_run': self.dry_run_checkbox.isChecked(),
            'delete': self.delete_checkbox.isChecked(),
            'compress': self.compress_checkbox.isChecked(),
            'verbose': self.verbose_checkbox.isChecked(),
            'exclude_patterns': self.exclude_input.text(),
            'bwlimit': self.bwlimit_input.value(),
        }

    def execute_scheduled_task(self, profile_data):
        # Restore settings
        self.source_input.setText(profile_data.get('source', ''))
        self.dest_input.setText(profile_data.get('destination', ''))
        self.source_type.setCurrentText(profile_data.get('source_type', 'Directory'))
        self.dest_type.setCurrentText(profile_data.get('dest_type', 'Directory'))
        self.dry_run_checkbox.setChecked(profile_data.get('dry_run', False))
        self.delete_checkbox.setChecked(profile_data.get('delete', False))
        self.compress_checkbox.setChecked(profile_data.get('compress', False))
        self.verbose_checkbox.setChecked(profile_data.get('verbose', False))
        self.exclude_input.setText(profile_data.get('exclude_patterns', ''))
        self.bwlimit_input.setValue(profile_data.get('bwlimit', 0))

        # Start sync
        self.start_sync()

    def load_profiles(self):
        """
        Loads available profiles into the profile combo box.

        This method reads the profile files from the profiles directory, extracts the profile names,
        and populates the profile combo box with these names.

        :return: None
        """
        self.profile_combo.clear()
        profiles = [f[:-5] for f in os.listdir(self.profiles_dir) if f.endswith(".json")]
        self.profile_combo.addItems(profiles)


    def save_profile(self):
        """
        Saves the current settings as a profile.

        This method prompts the user to enter a profile name, then saves the current settings
        (source, destination, options, etc.) to a JSON file in the profiles directory.

        :return: None
        """
        profile_name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if ok and profile_name:
            profile_data = {
                "source": self.source_input.text(),
                "destination": self.dest_input.text(),
                "source_type": self.source_type.currentText(),
                "dest_type": self.dest_type.currentText(),
                "dry_run": self.dry_run_checkbox.isChecked(),
                "delete": self.delete_checkbox.isChecked(),
                "compress": self.compress_checkbox.isChecked(),
                "verbose": self.verbose_checkbox.isChecked(),
                "exclude_patterns": self.exclude_input.text(),
                "bwlimit": self.bwlimit_input.value(),
            }
            profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
            with open(profile_path, "w") as f:
                json.dump(profile_data, f)
            QMessageBox.information(
                self, "Profile Saved", f"{profile_name} saved successfully"
            )
            self.load_profiles()


    def load_profile(self):
        """
        Loads the selected profile into the GUI.

        This method reads the selected profile from the profiles directory and updates the GUI
        with the settings stored in the profile.

        :return: None
        """
        profile_name = self.profile_combo.currentText()
        if profile_name:
            profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
            if os.path.exists(profile_path):
                with open(profile_path, "r") as f:
                    profile_data = json.load(f)
                    self.source_input.setText(profile_data.get("source", ""))
                    self.dest_input.setText(profile_data.get("destination", ""))
                    self.source_type.setCurrentText(
                        profile_data.get("source_type", "Directory")
                    )
                    self.dest_type.setCurrentText(
                        profile_data.get("dest_type", "Directory")
                    )
                    self.dry_run_checkbox.setChecked(profile_data.get("dry_run", False))
                    self.delete_checkbox.setChecked(profile_data.get("delete", False))
                    self.compress_checkbox.setChecked(profile_data.get("compress", False))
                    self.verbose_checkbox.setChecked(profile_data.get("verbose", False))
                    self.exclude_input.setText(profile_data.get("exclude_patterns", ""))
                    self.bwlimit_input.setValue(profile_data.get("bwlimit", 0))
                    QMessageBox.information(
                        self,
                        "Profile Loaded",
                        f"Profile '{profile_name}' loaded successfully.",
                    )


    def delete_profile(self):
        """
        Deletes the selected profile.

        This method prompts the user for confirmation before deleting the selected profile
        from the profiles directory.

        :return: None
        """
        profile_name = self.profile_combo.currentText()
        if profile_name:
            reply = QMessageBox.question(
                self,
                "Delete Profile",
                f"Are you sure you want to delete profile '{profile_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
                if os.path.exists(profile_path):
                    os.remove(profile_path)
                    QMessageBox.information(
                        self,
                        "Profile Deleted",
                        f"Profile '{profile_name}' deleted successfully.",
                    )
                    self.load_profiles()

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

    def start_sync(self):
        """
        Initiates the synchronization process using `rsync`. This method performs
        the following steps:

        1. Checks if `rsync` is available in the system's PATH.
        2. Validates the source and destination paths.
        3. Constructs the `rsync` command with appropriate options based on user inputs.
        4. Confirms with the user if the `--delete` option is selected.
        5. Executes the `rsync` command in a separate thread.

        :return: None if prerequisites are not met or user cancels deletion confirmation.
        """
        if shutil.which("rsync") is None:
            QMessageBox.critical(
                self, "Error", "Rsync is not installed or not found in PATH."
            )
            return
        if not self.validate_paths():
            return

        source = self.source_input.text()
        dest = self.dest_input.text()

        # Build the rsync command based on the selected options
        rsync_command = ["rsync", "-a"]  # '-a' is for archive mode

        # Bandwidth limit
        bwlimit_value = self.bwlimit_input.value()
        if bwlimit_value > 0:
            rsync_command.extend(["--bwlimit", str(bwlimit_value)])

        # Handle file or directory
        if self.source_type.currentText() == "File":
            rsync_command.remove("-a")  # Remove '-a' option for files
            rsync_command.append("-r")  # Recursively copy

        # Add options based on the selected checkboxes
        if self.dry_run_checkbox.isChecked():
            rsync_command.append("--dry-run")
        if self.delete_checkbox.isChecked():
            rsync_command.append("--delete")
        if self.compress_checkbox.isChecked():
            rsync_command.append("--compress")
        if self.verbose_checkbox.isChecked():
            rsync_command.append("--verbose")
            rsync_command.append("--progress")  # Add progress for verbose mode

        # Handle exclude patterns
        exclude_patterns = self.exclude_input.text()
        if exclude_patterns:
            patterns = [pattern.strip() for pattern in exclude_patterns.split(",")]

            for pattern in patterns:
                rsync_command.extend(["--exclude", pattern])

        rsync_command.extend([source, dest])

        # Confirm if '--delete' option is selected
        if self.delete_checkbox.isChecked():
            reply = QMessageBox.question(
                self,
                "Warning",
                "Are you sure you want to delete files in the destination that are not in the source?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        # Run rsync in separate thread
        self.run_rsync_thread(rsync_command)

    def run_rsync_thread(self, command):
        """
        :param command: The rsync command to execute in the thread.
        :return: None
        """
        # Create an instance of the Rsync Thread
        self.rsync_thread = RsyncThread(command)
        self.rsync_thread.output_signal.connect(self.update_output)
        self.rsync_thread.progress_signal.connect(self.update_progress)
        self.rsync_thread.error_signal.connect(self.rsync_error)
        self.rsync_thread.finished_signal.connect(self.rsync_finished)

        # Create output dialog
        self.output_dialog = QDialog(self)
        self.output_dialog.setWindowTitle("Rsync Output")
        dialog_layout = QVBoxLayout()
        self.output_dialog.setLayout(dialog_layout)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        dialog_layout.addWidget(self.output_text)

        self.progress_bar = QProgressBar()
        dialog_layout.addWidget(self.progress_bar)

        # Add Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_rsync)
        dialog_layout.addWidget(self.cancel_button)

        self.output_dialog.show()

        self.rsync_thread.start()

    def update_output(self, text):
        """
        :param self:
        :param text: The text to be appended to the output.
        :return: None
        """
        self.output_text.append(text)
        self.output_text.ensureCursorVisible()

    def update_progress(self, value):
        """
        :param self:
        :param value: The integer value to update the progress bar to.
        :return: None
        """
        self.progress_bar.setValue(value)

    def rsync_error(self, error_message):
        """
        :param self:
        :param error_message: A string containing the error message to be displayed in the critical message box.
        :return: None
        """
        QMessageBox.critical(self, "Error", error_message)
        self.tray_icon.showMessage(
            "Rsync Error", error_message, QSystemTrayIcon.Critical, 5000
        )
        self.output_dialog.close()

    def rsync_finished(self, success):
        """
        :param self:
        :param success: A boolean indicating if the rsync operation was successful.
        :return: None
        """
        if success:
            QMessageBox.information(
                self, "Success", "Rsync operation completed successfully."
            )
            self.tray_icon.showMessage(
                "Rsync Completed",
                "Rsync operation completed successfully.",
                QSystemTrayIcon.Information,
                5000,
            )
        self.output_dialog.close()

    def cancel_rsync(self):
        """
        Prompts the user with a warning message to confirm the cancellation of the rsync operation.
        If the user confirms and the rsync thread is running, waits for the thread to finish and closes the output dialog.

        :return: None
        """
        reply = QMessageBox.question(
            self,
            "Warning",
            "Are you sure you want to cancel the rsync operation?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            if self.rsync_thread.isRunning():
                self.rsync_thread.wait()
                self.output_dialog.close()
                QMessageBox.information(self, "Cancelled", "Rsync operation cancelled.")

    def load_stylesheet(self):
        # Load stylesheet from external .qss file
        qss_path = os.path.join(os.path.dirname(__file__), "resources", "styles.qss")
        with open(qss_path, "r") as file:
            self.setStyleSheet(file.read())


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     ex = SyncMateGUI()
#     ex.show()
#     sys.exit(app.exec())
