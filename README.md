
---

# SyncMate

**SyncMate** is a modern, user-friendly GUI tool built using Python and PyQt, designed to streamline file and directory synchronization with the powerful `rsync` command-line tool. Whether you need to back up large directories, sync files between different systems, or simply keep important documents up to date, SyncMate offers an intuitive interface that makes the process easy and visually appealing.

### Features
- **Simple, Modern Interface**: A sleek and modern UI powered by PyQt with customizable themes, including dark mode.
- **Browse Files and Directories**: Easily select both files and directories for synchronization through file dialogs.
- **Rsync Integration**: SyncMate leverages `rsync`'s power for efficient file transfers, backups, and synchronization.
- **Progress Tracking**: Real-time synchronization progress display with detailed transfer statistics.
- **Cross-Platform**: Works across Linux, macOS, and Windows (via WSL for rsync).
- **Customization**: Supports multiple rsync options including compression, deletion, and verbose modes.
- **FontAwesome Icons**: Incorporates beautiful icons from FontAwesome to enhance the user experience.
- **Lightweight & Fast**: Minimal dependencies ensure a lightweight tool that is fast and responsive.

### Planned Features
- **Scheduling Syncs**: Schedule automatic syncs for regular backups.
- **Cloud Support**: Future integration with cloud storage services like AWS S3, Google Drive, and Dropbox.
- **Profile Management**: Save frequently used sync configurations as profiles for quick access.
- **Notifications**: Desktop notifications upon sync completion or error.

### Installation
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Breedlove-Jason/SyncMate.git
cd SyncMate
pip install -r requirements.txt
```

### Usage
Run the app by executing:

```bash
python main.py
```

### Contributions
We welcome contributions from the open-source community! Feel free to fork the project, submit issues, and open pull requests. Let’s make SyncMate even better together.

### License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

---