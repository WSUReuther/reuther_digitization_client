import logging

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QPlainTextEdit


class WorkerSignals(QObject):
    finished = pyqtSignal()
    status = pyqtSignal(str)
    success = pyqtSignal(str)
    error = pyqtSignal(str)


class TaskWorker(QRunnable):

    def __init__(self, item, task):
        super().__init__()
        self.item = item
        self.task = task
        task_settings = self.get_task_settings()
        self.function = task_settings["function"]
        self.message = task_settings["message"]
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.signals.status.emit(f"{self.message} for {self.item.item_identifier}")
        task_function = self.function
        try:
            response = task_function()
            self.signals.success.emit(f"successfully finished {self.message} for {self.item.item_identifier}: {response}")
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

    def get_task_settings(self):
        task_settings = {
            "copy": {"function": self.item.copy_item_to_remote_dir, "message": "copying files"},
            "derivatives": {"function": self.item.generate_derivatives, "message": "generating derivatives"},
            "rename": {"function": self.item.rename_preservation_scans, "message": "renaming files"},
            "complete": {"function": self.item.check_complete, "message": "checking completeness"}
        }

        return task_settings[self.task]


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
