from functools import partial
import logging
import os

from reuther_digitization_utils.item_utils import ItemUtils

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
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
        # only filter box column
        self.allowed_filter_indexes = [2]
        self.scan_storage_location = DigitizationClient.config.get("scan_storage_location")

        self.tasks = ["rename", "derivatives", "copy", "complete"]
        self.task_labels = ["Rename Files", "Generate Derivatives", "Copy to HOLD", "Complete"]

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
        self.itemsTable.horizontalHeader().sectionClicked.connect(self.onHeaderClicked)
        self.itemsTable.setHorizontalHeaderLabels(["Title", "Dates", "Box", "Folder", "Identifier", "Rename", "Derivatives", "Copy", "Complete"])
        self.itemsTable.setAlternatingRowColors(True)
        self.itemsTable.setEditTriggers(QTableWidget.NoEditTriggers)
        items = get_project_items(project_id)
        row_position = 0
        for item in items:
            self.itemsTable.insertRow(row_position)
            self.row_to_item_ids[row_position] = item["id"]
            item_title = item["title"]
            item_dates = item["dates"]
            # hack until I figure out why Qt is removing spaces after commas
            item_title_spaces = item_title.replace(", ", ",  ")
            item_dates_spaces = item_dates.replace(", ", ",  ")
            self.itemsTable.setItem(row_position, 0, QTableWidgetItem(item_title_spaces))
            self.itemsTable.setItem(row_position, 1, QTableWidgetItem(item_dates_spaces))
            self.itemsTable.setItem(row_position, 2, QTableWidgetItem(item["box"]))
            self.itemsTable.setItem(row_position, 3, QTableWidgetItem(item["folder"]))
            self.itemsTable.setItem(row_position, 4, QTableWidgetItem(item["identifier"]))
            task_widgets = self.make_task_widgets(row_position, item)
            task_widget_range = len(task_widgets)
            col_start = 5
            col_end = col_start + task_widget_range
            for task_i, col_i in zip(list(range(task_widget_range)), list(range(col_start, col_end))):
                self.itemsTable.setCellWidget(row_position, col_i, task_widgets[task_i])
            row_position += 1
        self.keywords = dict([(i, []) for i in range(self.itemsTable.columnCount())])
        self.itemsTable.resizeColumnsToContents()

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

            headerPos = self.itemsTable.mapToGlobal(self.itemsTable.horizontalHeader().pos())
            posY = headerPos.y() + self.itemsTable.horizontalHeader().height()
            posX = headerPos.x() + self.itemsTable.horizontalHeader().sectionPosition(index)
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
            self.itemsTable.removeCellWidget(row_position, column)
            self.itemsTable.setCellWidget(row_position, column, task_label)
        if remaining_tasks > 0:
            self.row_buttons[row_position][0].setEnabled(True)
            for button in self.row_buttons[row_position][1:]:
                button.setEnabled(False)

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
        identifier = self.itemsTable.item(row_position, 4).text()
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
            page_count = len(os.listdir(item.tiffs_dir))
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