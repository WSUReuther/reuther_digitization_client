# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'items.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Items(object):
    def setupUi(self, Items):
        Items.setObjectName("Items")
        Items.resize(1000, 700)
        self.gridLayout = QtWidgets.QGridLayout(Items)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.itemsTable = QtWidgets.QTableWidget(Items)
        self.itemsTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.itemsTable.setColumnCount(10)
        self.itemsTable.setObjectName("itemsTable")
        self.itemsTable.setRowCount(0)
        self.verticalLayout.addWidget(self.itemsTable)
        self.projectsBtn = QtWidgets.QPushButton(Items)
        self.projectsBtn.setObjectName("projectsBtn")
        self.verticalLayout.addWidget(self.projectsBtn)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.loggerLayout = QtWidgets.QVBoxLayout()
        self.loggerLayout.setObjectName("loggerLayout")
        self.verticalLayout_2.addLayout(self.loggerLayout)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Items)
        QtCore.QMetaObject.connectSlotsByName(Items)

    def retranslateUi(self, Items):
        _translate = QtCore.QCoreApplication.translate
        Items.setWindowTitle(_translate("Items", "Items"))
        self.projectsBtn.setText(_translate("Items", "Back to Projects"))
