from functools import partial
import logging
import os
import subprocess

from reuther_digitization_utils.item_utils import ItemUtils

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QWidgetAction
)

from reuther_digitization_client.database import (
    get_item_progress,
    get_project_items,
    reset_task_progress,
    update_item_page_count,
    update_item_progress
)
from reuther_digitization_client.helpers import TaskWorker, QTextEditLogger

from reuther_digitization_client.ui.items import Ui_Items


class Items(QWidget, Ui_Items):
    def __init__(self, DigitizationClient, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.digitization_client = DigitizationClient
        self.projectsBtn.clicked.connect(self.digitization_client.show_projects)
        self.project_dir = None
        self.row_buttons = {}
        self.row_to_item_ids = {}
        self.row_to_item_identifiers = {}
        # only filter box column
        self.allowed_filter_indexes = [1]
        self.scan_storage_location = DigitizationClient.config.get("scan_storage_location")

        generate_derivatives = DigitizationClient.config.get("generate_derivatives")
        if generate_derivatives:
            self.tasks = ["rename", "derivatives", "copy", "complete"]
            self.task_labels = ["Rename Files", "Generate Derivatives", "Copy to HOLD", "Complete"]
            self.headers = ["Title/Dates", "Box", "Folder", "Identifier", "Open", "Rename", "Derivatives", "Copy", "Complete", "Reset"]
        else:
            self.tasks = ["rename", "copy", "complete"]
            self.task_labels = ["Rename Files", "Copy to HOLD", "Complete"]
            self.headers = ["Title/Dates", "Box", "Folder", "Identifier", "Open", "Rename", "Copy", "Complete", "Reset"]

        logTextBox = QTextEditLogger(self)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        logTextBox.setFormatter(formatter)
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)
        self.loggerLayout.addWidget(logTextBox.widget)

    def load_items(self, project_id, project_dir):
        self.project_dir = project_dir
        self.itemsTable.clear()
        self.itemsTable.setRowCount(0)
        self.horizontalHeader = self.itemsTable.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.onHeaderClicked)
        self.itemsTable.setHorizontalHeaderLabels(self.headers)
        self.itemsTable.setAlternatingRowColors(True)
        self.itemsTable.setEditTriggers(QTableWidget.NoEditTriggers)
        items = get_project_items(project_id)
        row_position = 0
        for item in items:
            self.itemsTable.insertRow(row_position)
            self.row_to_item_ids[row_position] = item["id"]
            item_identifier = item["identifier"]
            self.row_to_item_identifiers[row_position] = item_identifier
            display_string = item["display_string"]
            # hack until I figure out why Qt is removing spaces after commas
            display_string = display_string.replace(", ", ",  ")
            self.itemsTable.setItem(row_position, 0, QTableWidgetItem(display_string))
            self.itemsTable.setItem(row_position, 1, QTableWidgetItem(item["box"]))
            self.itemsTable.setItem(row_position, 2, QTableWidgetItem(item["folder"]))
            self.itemsTable.setItem(row_position, 3, QTableWidgetItem(item["identifier"]))
            item_dir = os.path.join(self.project_dir, item_identifier)
            openDirBtn = QPushButton("Open")
            openDirBtn.clicked.connect(partial(self.try_open_folder, item_dir))
            self.itemsTable.setCellWidget(row_position, 4, openDirBtn)
            task_widgets = self.make_task_widgets(row_position, item)
            task_widget_range = len(task_widgets)
            col_start = 5
            col_end = col_start + task_widget_range
            for task_i, col_i in zip(list(range(task_widget_range)), list(range(col_start, col_end))):
                self.itemsTable.setCellWidget(row_position, col_i, task_widgets[task_i])
            resetItemBtn = QPushButton("Reset")
            resetItemBtn.clicked.connect(partial(self.reset_item, row_position))
            self.itemsTable.setCellWidget(row_position, col_end, resetItemBtn)
            row_position += 1
        self.keywords = dict([(i, []) for i in range(self.itemsTable.columnCount())])
        self.horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)
        for i in range(1, 10):
            self.horizontalHeader.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.itemsTable.resizeColumnsToContents()

    def try_open_folder(self, directory):
        if os.path.exists(directory):
            subprocess.call(["open", directory])
        else:
            logging.error(f"Directory does not exist: {directory}")

    def onHeaderClicked(self, index):
        # only filter box column
        if index in self.allowed_filter_indexes:
            self.menu = QMenu(self)
            self.col = index
            data_unique = []
            self.checkBoxes = []

            deselectBtn = QPushButton("Deselect all")
            deselectBtn.clicked.connect(self.deselectAll)
            deselectAction = QWidgetAction(self.menu)
            deselectAction.setDefaultWidget(deselectBtn)
            self.menu.addAction(deselectAction)

            for i in range(self.itemsTable.rowCount()):
                item = self.itemsTable.item(i, index)
                if item.text() not in data_unique:
                    data_unique.append(item.text())
                    checkbox = QCheckBox(item.text(), self.menu)
                    checkbox.setChecked(not self.itemsTable.isRowHidden(i))
                    checkableAction = QWidgetAction(self.menu)
                    checkableAction.setDefaultWidget(checkbox)
                    self.menu.addAction(checkableAction)
                    self.checkBoxes.append(checkbox)

            dialogBtn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                        Qt.Horizontal, self.menu)

            dialogBtn.accepted.connect(self.filterAndClose)
            dialogBtn.rejected.connect(self.menu.close)
            checkableAction = QWidgetAction(self.menu)
            checkableAction.setDefaultWidget(dialogBtn)
            self.menu.addAction(checkableAction)

            clearBtn = QPushButton("Clear filter")
            clearBtn.clicked.connect(self.clearFilter)
            clearAction = QWidgetAction(self.menu)
            clearAction.setDefaultWidget(clearBtn)
            self.menu.addAction(clearAction)

            headerPos = self.itemsTable.mapToGlobal(self.horizontalHeader.pos())
            posY = headerPos.y() + self.horizontalHeader.height()
            posX = headerPos.x() + self.horizontalHeader.sectionPosition(index)
            self.menu.exec_(QPoint(posX, posY))

    def deselectAll(self):
        for checkbox in self.checkBoxes:
            checkbox.setChecked(False)

    def clearFilter(self):
        for i in range(self.itemsTable.rowCount()):
            self.itemsTable.setRowHidden(i, False)
        self.menu.close()

    def filterAndClose(self):
        self.keywords[self.col] = []
        for element in self.checkBoxes:
            if element.isChecked():
                self.keywords[self.col].append(element.text())
        self.filterdata()
        self.menu.close()

    def filterdata(self):
        columnsShow = dict([(i, True) for i in range(self.itemsTable.rowCount())])
        for i in range(self.itemsTable.rowCount()):
            for j in self.allowed_filter_indexes:
                if self.keywords[j]:
                    item = self.itemsTable.item(i, j)
                    if item.text() not in self.keywords[j]:
                        columnsShow[i] = False
        for key, value in columnsShow.items():
            self.itemsTable.setRowHidden(key, not value)

    def make_task_widgets(self, row_position, item):
        task_widgets = []
        buttons = []
        completed_tasks = self.count_completed_tasks(item)
        for i in range(completed_tasks):
            task_label = self.make_task_complete_label()
            task_widgets.append(task_label)
        for i in range(completed_tasks, len(self.tasks)):
            task = self.tasks[i]
            label = self.task_labels[i]
            button = QPushButton(label)
            if i == completed_tasks:
                button.setEnabled(True)
            else:
                button.setEnabled(False)
            button.clicked.connect(partial(self.start_worker, task, row_position))
            task_widgets.append(button)
            buttons.append(button)
        self.row_buttons[row_position] = buttons
        return task_widgets

    def set_task_states(self, item, row_position):
        completed_tasks = self.count_completed_tasks(item)
        remaining_tasks = len(self.tasks) - completed_tasks
        difference = len(self.row_buttons[row_position]) - remaining_tasks
        self.row_buttons[row_position] = self.row_buttons[row_position][difference:]
        for i in range(completed_tasks):
            column = i + 5
            task_label = self.make_task_complete_label()
            self.itemsTable.setCellWidget(row_position, column, task_label)
        if remaining_tasks > 0:
            self.row_buttons[row_position][0].setEnabled(True)
            for button in self.row_buttons[row_position][1:]:
                button.setEnabled(False)

    def reset_item(self, row_position):
        item_id = self.row_to_item_ids[row_position]
        reset_task_progress(item_id)
        item_progress = dict((task, 0) for task in self.tasks)
        task_widgets = self.make_task_widgets(row_position, item_progress)
        for i, widget in enumerate(task_widgets):
            column = i + 5
            self.itemsTable.setCellWidget(row_position, column, widget)

    def make_task_complete_label(self):
        task_complete_label = QLabel("✓")
        task_complete_label.setAlignment(Qt.AlignCenter)
        return task_complete_label

    def count_completed_tasks(self, item):
        completed_tasks = 0
        for task in self.tasks:
            if item[task] == 1:
                completed_tasks += 1
        return completed_tasks

    def start_worker(self, task, row_position):
        item_id = self.row_to_item_ids[row_position]
        identifier = self.row_to_item_identifiers[row_position]
        project_dir = self.project_dir
        collection_id = os.path.basename(project_dir)
        remote_scans_dir = os.path.join(self.scan_storage_location, collection_id)
        item = ItemUtils(project_dir, identifier, remote_scans_dir=remote_scans_dir)

        self.worker = TaskWorker(item, task)
        self.worker.signals.error.connect(self.report_error)
        self.worker.signals.status.connect(self.report_progress)
        self.worker.signals.success.connect(self.report_success)
        self.worker.signals.success.connect(partial(self.update_db_on_success, row_position, task, item))
        self.digitization_client.threadpool.start(self.worker)

        self.disable_row_buttons(row_position)
        if self.projectsBtn.isEnabled():
            self.projectsBtn.setEnabled(False)
        self.worker.signals.finished.connect(partial(self.set_task_states_after_thread, row_position, item_id))

    def update_db_on_success(self, row_position, task, item):
        item_id = self.row_to_item_ids[row_position]
        update_item_progress(item_id, task)
        if task == "rename":
            page_count = len(item.get_tiff_filepaths())
            update_item_page_count(item_id, page_count)

    def set_task_states_after_thread(self, row_position, item_id):
        if self.digitization_client.threadpool.activeThreadCount() == 0:
            self.projectsBtn.setEnabled(True)
        item_progress = get_item_progress(item_id)
        self.set_task_states(item_progress, row_position)

    def disable_row_buttons(self, row_position):
        for button in self.row_buttons[row_position]:
            button.setEnabled(False)

    def report_success(self, message):
        logging.info(message)

    def report_progress(self, message):
        logging.info(message)

    def report_error(self, message):
        logging.error(message)
