from PySide6.QtCore import QThread, Signal

class RsyncThread(QThread):
    output_signal = Signal(str)
    progress_signal = Signal(int)
    error_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None
        self.is_running = True

    def run(self):
        import subprocess

        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,)

            total_files = None
            for line in self.process.stdout:
                if not self.is_running:
                    self.process.terminate()
                    break

                self.output_signal.emit(line.strip())

                if "to-check" in line:
                    try:
                        to_check = int(line.split("to-check=")[1].split("/")[0])
                        total = int(line.split("to-check=")[1].split("/")[1])
                        if total_files is None:
                            total_files = total

                        files_transferred = total - to_check
                        progress = int((files_transferred / total_files) * 100)
                        self.progress_signal.emit(progress)
                    except:
                        pass
            self.process.wait()
            if self.process.returncode == 0:
                self.finished_signal.emit(True)
            else:
                self.error_signal.emit(f"Rsync exited with code {self.process.returncode}")
        except Exception as e:
            self.error_signal.emit(str(e))