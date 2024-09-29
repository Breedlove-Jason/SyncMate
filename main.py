import sys
from PySide6.QtWidgets import QApplication
from gui import SyncMateGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SyncMateGUI()
    ex.show()
    app.aboutToQuit.connect(ex.tray_icon.hide)
    sys.exit(app.exec())