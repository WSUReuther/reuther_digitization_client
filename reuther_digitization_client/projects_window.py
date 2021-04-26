import os

from functools import partial
from PyQt5.QtWidgets import (
        QDialog,
        QFileDialog,
        QMessageBox,
        QPushButton,
        QTableWidgetItem,
        QWidget
    )

from reuther_digitization_client.database import create_item, create_project, get_projects
from reuther_digitization_utils.project_utils import ProjectUtils

from reuther_digitization_client.ui.add_project_dialog import Ui_createProject
from reuther_digitization_client.ui.projects import Ui_Projects


class Projects(QWidget, Ui_Projects):
    def __init__(self, DigitizationClient, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.addProjectBtn.clicked.connect(self.add_project)
        self.load_projects()
        self.digitization_client = DigitizationClient

    def load_projects(self):
        self.projectsTable.clear()
        self.projectsTable.setRowCount(0)
        self.projectsTable.setHorizontalHeaderLabels(["id", "Collection ID", "Name", "Project Directory", "Total Items", "Completed Items", "Total Scans", "Load"])
        projects = get_projects()
        row_position = 0
        for project in projects:
            self.projectsTable.insertRow(row_position)
            self.btn_load = QPushButton("Load Project")
            self.projectsTable.setItem(row_position, 0, QTableWidgetItem(str(project["id"])))
            self.projectsTable.setItem(row_position, 1, QTableWidgetItem(project["collection_id"]))
            self.projectsTable.setItem(row_position, 2, QTableWidgetItem(project["name"]))
            self.projectsTable.setItem(row_position, 3, QTableWidgetItem(project["project_dir"]))
            self.projectsTable.setItem(row_position, 4, QTableWidgetItem(str(project["total_items"])))
            self.projectsTable.setItem(row_position, 5, QTableWidgetItem(str(project["completed_items"])))
            self.projectsTable.setItem(row_position, 6, QTableWidgetItem(str(project["total_scans"])))
            self.projectsTable.setCellWidget(row_position, 7, self.btn_load)
            self.btn_load.clicked.connect(partial(self.load_project, project["id"], project["project_dir"]))
            row_position += 1
        self.projectsTable.resizeColumnsToContents()

    def add_project(self):
        dialog = AddProject(self)
        dialog.exec()

    def load_project(self, project_id, project_dir):
        self.digitization_client.load_items(project_id, project_dir)


class AddProject(QDialog, Ui_createProject):
    def __init__(self, Projects, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.inputSpreadsheetBtn.clicked.connect(self.browse_spreadsheet)
        self.outputDirBtn.clicked.connect(self.browse_output_dir)
        self.importBtn.clicked.connect(self.import_project)
        self.cancelButton.clicked.connect(self.reject)
        self.digitization_client = Projects.digitization_client
        default_output_dir = self.digitization_client.config.get("output_dir")
        if default_output_dir:
            self.outputDir.setText(default_output_dir)

    def browse_spreadsheet(self):
        self.inputSpreadsheet.clear()
        spreadsheet, _filter = QFileDialog.getOpenFileName(self, "Select a CSV")
        if spreadsheet:
            self.inputSpreadsheet.setText(spreadsheet)

    def browse_output_dir(self):
        self.outputDir.clear()
        directory = QFileDialog.getExistingDirectory(self, "Select directory")
        if directory:
            self.outputDir.setText(directory)

    def import_project(self):
        run_import = True
        project_name = self.projectName.text()
        input_spreadsheet = self.inputSpreadsheet.text()
        if not os.path.exists(input_spreadsheet):
            QMessageBox.information(self, "Error", f"Could not find spreadsheet {input_spreadsheet}. Please select an input spreadsheet")
            run_import = False
        output_dir = self.outputDir.text()
        if not os.path.exists(output_dir):
            QMessageBox.information(self, "Error", f"Could not find directory {output_dir}. Please select an output directory")
            run_import = False
        if run_import:
            project = ProjectUtils(output_dir, input_spreadsheet)
            project_dir = project.collection_dir
            collection_id = project.collection_id
            project.setup_project()
            project_id = create_project(collection_id, project_name, project_dir)
            for item in project.items:
                create_item(item, project_id)
            self.digitization_client.load_items(project_id, project_dir)
            self.accept()
