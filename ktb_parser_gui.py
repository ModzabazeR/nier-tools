import sys
import json
import lib.unicodetools as ut
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QTableWidget, QTableWidgetItem,
                             QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QProgressBar, 
                             QLineEdit, QComboBox, QLabel, QStyledItemDelegate, QMenu, QAbstractItemView)
from PyQt5.QtGui import QColor, QFont, QDrag
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData

class DraggableTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def dropEvent(self, event):
        source_index = self.currentRow()
        target_index = self.indexAt(event.pos()).row()

        if target_index < 0 or target_index == source_index:
            return

        # Swap the rows in the table
        for column in range(self.columnCount()):
            source_item = self.takeItem(source_index, column)
            target_item = self.takeItem(target_index, column)
            self.setItem(source_index, column, target_item)
            self.setItem(target_index, column, source_item)

        event.accept()

class UnicodeTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self.updateTooltip()

    def setText(self, text):
        super().setText(text)
        self.updateTooltip()

    def updateTooltip(self):
        text = self.text()
        try:
            if text.startswith("0x"):
                text = chr(int(text, 16))
            self.setToolTip(f"Dec: <b>{ord(text):d}</b> Hex: <b>{ord(text):04x}</b>")
        except (ValueError, TypeError):
            self.setToolTip("Invalid Unicode")

class FileLoader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        kerning_list = self.parse_ktb(self.file_path)
        self.finished.emit(kerning_list)

    def parse_ktb(self, file_path, is_tranform: bool = True):
        def read_int(reader, num_bytes):
            return int.from_bytes(reader.read(num_bytes), byteorder='little', signed=True)

        def read_utf16(reader, num_bytes):
            return reader.read(num_bytes).decode('utf-16le')

        with open(file_path, 'rb') as reader:
            count = read_int(reader, 2)
            kerning_list = []
            for i in range(count):
                left = read_utf16(reader, 2)
                right = read_utf16(reader, 2)
                kerning = read_int(reader, 2)

                if is_tranform:
                    for k, v in ut.UNICODE_MAP.items():
                        if left == v:
                            left = k
                        if right == v:
                            right = k

                kerning_entry = {
                    "first_character": left,
                    "second_character": right,
                    "kerning": kerning
                }
                kerning_list.append(kerning_entry)
                self.progress.emit(int((i + 1) / count * 100))
        return kerning_list

class KTBParserGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.kerning_list = []
        self.current_file_path = None

    def initUI(self):
        self.setWindowTitle('KTB Parser - untitled.ktb')
        self.setGeometry(100, 100, 800, 600)

        # Set font for the entire application
        font = QFont()
        font.setPointSize(12)

        # Menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')

        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.triggered.connect(self.openFileDialog)
        fileMenu.addAction(openFile)

        saveFile = QAction('Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.triggered.connect(self.saveFile)
        fileMenu.addAction(saveFile)

        saveFileAs = QAction('Save As', self)
        saveFileAs.setShortcut('Ctrl+Shift+S')
        saveFileAs.triggered.connect(self.saveFileAsDialog)
        fileMenu.addAction(saveFileAs)

        importJson = QAction('Import JSON', self)
        importJson.setShortcut('Ctrl+I')
        importJson.triggered.connect(self.importJsonFileDialog)
        fileMenu.addAction(importJson)

        exportJson = QAction('Export as JSON', self)
        exportJson.setShortcut('Ctrl+E')
        exportJson.triggered.connect(self.exportJsonFileDialog)
        fileMenu.addAction(exportJson)

        closeFile = QAction('Close File', self)
        closeFile.setShortcut('Ctrl+W')
        closeFile.triggered.connect(self.closeFile)
        fileMenu.addAction(closeFile)

        # Sort by first character's unicode action
        sortAction = QAction('Sort Table', self)
        sortAction.triggered.connect(self.sortTable)
        fileMenu.addAction(sortAction)

        # Duplicate row action
        duplicateRowAction = QAction('Duplicate Row', self)
        duplicateRowAction.setFont(font)
        duplicateRowAction.setShortcut('Ctrl+D')
        duplicateRowAction.triggered.connect(self.duplicateSelectedRow)
        self.addAction(duplicateRowAction)

        # Table widget to display kerning data
        self.tableWidget = DraggableTableWidget()
        self.tableWidget.setFont(font)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['First Character', 'Second Character', 'Kerning'])
        # set column to fill the space equally
        for i in range(3): self.tableWidget.horizontalHeader().setSectionResizeMode(i, 1)
        self.tableWidget.horizontalHeader().setFont(font)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.showContextMenu)

        # Search bar and combo box for column selection
        self.searchBar = QLineEdit()
        self.searchBar.setStyleSheet("padding: 5px 10px;")
        self.searchBar.setPlaceholderText("Search...")
        self.searchBar.textChanged.connect(self.searchTable)

        self.searchComboBox = QComboBox()
        self.searchComboBox.setStyleSheet("QComboBox { padding: 5px 10px; } QComboBox QAbstractItemView::item { height: 30px; }")
        self.searchComboBox.setItemDelegate(QStyledItemDelegate())
        self.searchComboBox.addItems(["First Character", "Second Character", "Kerning"])

        # Connect the itemChanged signal to the checkForDuplicates method
        self.tableWidget.itemChanged.connect(self.checkForDuplicates)
        self.tableWidget.itemChanged.connect(self.checkUnicode)

        # Add row button
        self.addRowButton = QPushButton('Add Row')
        self.addRowButton.setFixedHeight(40)
        self.addRowButton.clicked.connect(self.addRow)

        # Delete row button
        self.deleteRowButton = QPushButton('Delete Row')
        self.deleteRowButton.setFixedHeight(40)
        self.deleteRowButton.clicked.connect(self.deleteRow)

        # Save button
        self.saveButton = QPushButton('Save')
        self.saveButton.setFixedHeight(40)
        self.saveButton.clicked.connect(self.saveFile)

        # Progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)

        # Layout for search bar and combo box
        searchLayout = QHBoxLayout()
        searchLayout.addWidget(QLabel("Search:"))
        searchLayout.addWidget(self.searchBar)
        searchLayout.addWidget(QLabel("in"))
        searchLayout.addWidget(self.searchComboBox)

        # Layout for add and delete row buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.addRowButton)
        buttonLayout.addWidget(self.deleteRowButton)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(searchLayout)
        layout.addWidget(self.tableWidget)
        layout.addWidget(self.progressBar)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.saveButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def openFileDialog(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open KTB File', '', 'KTB Files (*.ktb);;All Files (*)', options=options)
        if filePath:
            self.current_file_path = filePath
            self.loadFile(filePath)
            self.setWindowTitleWithFilePath()

    def loadFile(self, file_path):
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        self.thread = FileLoader(file_path)
        self.thread.progress.connect(self.updateProgress)
        self.thread.finished.connect(self.loadTable)
        self.thread.start()

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def loadTable(self, kerning_list):
        self.kerning_list = kerning_list
        self.progressBar.setVisible(False)
        
        # Temporarily disconnect the itemChanged signal to prevent it from firing during table population
        self.tableWidget.itemChanged.disconnect(self.checkForDuplicates)
        
        self.tableWidget.setRowCount(len(self.kerning_list))
        for i, entry in enumerate(self.kerning_list):
            self.setTableItem(i, 0, entry['first_character'])
            self.setTableItem(i, 1, entry['second_character'])
            self.setTableItem(i, 2, str(entry['kerning']))

        # Reconnect the itemChanged signal after table population
        self.tableWidget.itemChanged.connect(self.checkForDuplicates)
        self.tableWidget.scrollToBottom()

    def addDragButton(self, row):
        button = QPushButton('☰')
        button.setFont(self.font())
        button.pressed.connect(lambda: self.startDrag(row))
        self.tableWidget.setCellWidget(row, 0, button)

    def startDrag(self, row):
        self.tableWidget.selectRow(row)
        drag = QDrag(self.tableWidget)
        mime_data = QMimeData()
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)

    def setTableItem(self, row, column, text):
        item = UnicodeTableWidgetItem(text) if column in [0, 1] else QTableWidgetItem(text)
        item.setFont(self.font())
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(row, column, item)

    def saveFile(self):
        if self.current_file_path:
            reply = QMessageBox.question(self, 'Save File', 'Do you want to save over the original file?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.collectTableData()
                self.save_ktb(self.current_file_path)
                self.setWindowTitleWithFilePath()
                QMessageBox.information(self, "Saved", "File saved successfully")
            else:
                self.saveFileAsDialog()
        else:
            self.saveFileAsDialog()

    def saveFileAsDialog(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, 'Save KTB File As', '', 'KTB Files (*.ktb);;All Files (*)', options=options)
        if filePath:
            self.collectTableData()
            self.save_ktb(filePath)
            self.current_file_path = filePath
            self.setWindowTitleWithFilePath()
            QMessageBox.information(self, "Saved", "File saved successfully")

    def addRow(self):
        selected_row = self.tableWidget.currentRow()
        is_last_row = selected_row == self.tableWidget.rowCount() - 1
        if selected_row == -1:
            # If no row is selected, add the row at the bottom
            rowPosition = self.tableWidget.rowCount()
        else:
            # Insert the new row after the selected row
            rowPosition = selected_row + 1
            
        self.tableWidget.insertRow(rowPosition)
        self.kerning_list.insert(rowPosition, {'first_character': '', 'second_character': '', 'kerning': 0})
        self.setTableItem(rowPosition, 0, '')
        self.setTableItem(rowPosition, 1, '')
        self.setTableItem(rowPosition, 2, '0')
        if is_last_row:
            self.tableWidget.scrollToBottom()

    def deleteRow(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            self.tableWidget.removeRow(selected_row)
            del self.kerning_list[selected_row]

    def checkForDuplicates(self, item):
        if item.column() in [0, 1]:  # Check only if the changed item is in the first or second character column
            row = item.row()
            
            first_char_item = self.tableWidget.item(row, 0)
            second_char_item = self.tableWidget.item(row, 1)

            # Ensure both items are created
            if first_char_item is None:
                first_char_item = QTableWidgetItem('')
                self.tableWidget.setItem(row, 0, first_char_item)
            if second_char_item is None:
                second_char_item = QTableWidgetItem('')
                self.tableWidget.setItem(row, 1, second_char_item)

            first_char = first_char_item.text() if first_char_item else ''
            second_char = second_char_item.text() if second_char_item else ''
            
            duplicate_found = False
            for r in range(self.tableWidget.rowCount()):
                if r != row:
                    existing_first_char = self.tableWidget.item(r, 0).text() if self.tableWidget.item(r, 0) else ''
                    existing_second_char = self.tableWidget.item(r, 1).text() if self.tableWidget.item(r, 1) else ''
                    if first_char == existing_first_char and second_char == existing_second_char:
                        duplicate_found = True
                        break
            
            color = QColor(Qt.red) if duplicate_found else QColor(Qt.white)
            self.tableWidget.item(row, 0).setBackground(color)
            self.tableWidget.item(row, 1).setBackground(color)

    def save_ktb(self, file_path, is_transform: bool = True):
        def write_int(value, num_bytes):
            return value.to_bytes(num_bytes, byteorder='little', signed=True)

        def write_utf16(value, num_bytes):
            return value.encode('utf-16le')

        with open(file_path, 'wb') as writer:
            count = len(self.kerning_list)
            writer.write(write_int(count, 2))

            if is_transform:
                for entry in self.kerning_list:
                    try:
                        writer.write(write_utf16(ut.UNICODE_MAP[entry['first_character']], 2))
                    except KeyError:
                        writer.write(write_utf16(entry['first_character'], 2))
                    try:
                        writer.write(write_utf16(ut.UNICODE_MAP[entry['second_character']], 2))
                    except KeyError:
                        writer.write(write_utf16(entry['second_character'], 2))
                    writer.write(write_int(entry['kerning'], 2))
            else:
                for entry in self.kerning_list:
                    writer.write(write_utf16(entry['first_character'], 2))
                    writer.write(write_utf16(entry['second_character'], 2))
                    writer.write(write_int(entry['kerning'], 2))

    def collectTableData(self):
        self.kerning_list = []
        for row in range(self.tableWidget.rowCount()):
            first_character = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ''
            second_character = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ''
            kerning = int(self.tableWidget.item(row, 2).text()) if self.tableWidget.item(row, 2) else 0
            self.kerning_list.append({
                'first_character': first_character,
                'second_character': second_character,
                'kerning': kerning
            })

    def searchTable(self, text: str):
        search_column = self.searchComboBox.currentIndex()

        if text.startswith("0x") and len(text) == 6:
            try:
                text = chr(int(text, 16))
                self.searchBar.setText(text)
            except ValueError:
                text = ''

        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, search_column)
            if item and text.lower() in item.text().lower():
                self.tableWidget.showRow(row)
            else:
                self.tableWidget.hideRow(row)


    def importJsonFileDialog(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open JSON File', '', 'JSON Files (*.json);;All Files (*)', options=options)
        if filePath:
            self.importJsonFile(filePath)

    def importJsonFile(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            print(f"Importing {len(data)} entries from {file_path}")
            for entry in data:
                first_character = chr(entry['first_unicode'])
                second_character = chr(entry['second_unicode'])
                kerning = entry['amount']
                self.appendRow(first_character, second_character, kerning)
            print(f"Imported {len(data)} entries")

    def appendRow(self, first_character, second_character, kerning):
        MULTIPLIER = 1
        new_kerning = round(int(kerning) / MULTIPLIER)
        if new_kerning == 0:
            if kerning > 0:
                new_kerning = 1
            elif kerning < 0:
                new_kerning = -1
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        self.setTableItem(rowPosition, 0, first_character)
        self.setTableItem(rowPosition, 1, second_character)
        self.setTableItem(rowPosition, 2, str(new_kerning))
        self.kerning_list.append({
            'first_character': first_character,
            'second_character': second_character,
            'kerning': new_kerning
        })
        self.tableWidget.scrollToBottom()

    def exportJsonFileDialog(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, 'Save JSON File As', '', 'JSON Files (*.json);;All Files (*)', options=options)
        if filePath:
            self.exportJsonFile(filePath)

    def exportJsonFile(self, file_path):
        data = []
        for entry in self.kerning_list:
            data.append({
                'amount': entry['kerning'],
                'first_unicode': ord(entry['first_character']),
                'second_unicode': ord(entry['second_character'])
            })
        with open(file_path, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        QMessageBox.information(self, "Exported", "File exported successfully")

    def closeFile(self):
        self.tableWidget.setRowCount(0)
        self.kerning_list = []
        self.current_file_path = None
        self.setWindowTitleWithFilePath()
        QMessageBox.information(self, "Closed", "File closed successfully")

    def checkUnicode(self, item):
        text = item.text()
        if text.startswith("0x"):
            try:
                text = chr(int(text, 16))
            except ValueError:
                text = ''
            item.setText(text)
        else:
            item.setText(text)
    
    def showContextMenu(self, position):
        contextMenu = QMenu(self)
        duplicateAction = contextMenu.addAction("Duplicate Row")
        duplicateAction.setShortcut("Ctrl+D")
        action = contextMenu.exec_(self.tableWidget.viewport().mapToGlobal(position))
        if action == duplicateAction:
            self.duplicateRow(self.tableWidget.indexAt(position).row())

    def duplicateRow(self, row):
        if row < 0:
            return
        first_character = self.tableWidget.item(row, 0).text()
        second_character = self.tableWidget.item(row, 1).text()
        kerning = self.tableWidget.item(row, 2).text()
        self.appendRow(first_character, second_character, int(kerning))

    def duplicateSelectedRow(self):
        selected_row = self.tableWidget.currentRow()
        self.duplicateRow(selected_row)

    def sortTable(self):
        self.collectTableData()
        self.kerning_list.sort(key=lambda x: (ord(x['first_character']) if x['first_character'] else -1,
                                            ord(x['second_character']) if x['second_character'] else -1))
        self.loadTable(self.kerning_list)

    def setWindowTitleWithFilePath(self):
        if self.current_file_path:
            self.setWindowTitle(f'KTB Parser - {self.current_file_path}')
        else:
            self.setWindowTitle('KTB Parser - untitled.ktb')

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = KTBParserGUI()
    ex.show()
    sys.exit(app.exec_())
