#!/usr/bin/env python

import sys

from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

from reuther_digitization_client.config import load_config
from reuther_digitization_client.database import create_connection
from reuther_digitization_client.items_window import Items
from reuther_digitization_client.projects_window import Projects

from reuther_digitization_client.ui.application_window import Ui_ApplicationWindow


class DigitizationClient(QMainWindow, Ui_ApplicationWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.config = load_config()
        self.threadpool = QThreadPool()

        self.projects = Projects(self)
        self.stackedWidget.addWidget(self.projects)

        self.items = Items(self)
        self.stackedWidget.addWidget(self.items)

    def show_projects(self):
        self.projects.load_projects()
        self.stackedWidget.setCurrentIndex(0)

    def load_items(self, project_id, project_dir):
        self.items.load_items(project_id, project_dir)
        self.stackedWidget.setCurrentIndex(1)
        QTimer.singleShot(150, self.adjustSize)


def main():
    app = QApplication(sys.argv)
    if not create_connection():
        sys.exit(1)
    form = DigitizationClient()
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
