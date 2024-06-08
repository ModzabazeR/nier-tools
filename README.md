# KTB Parser GUI

This project provides a Graphical User Interface (GUI) for parsing and editing KTB files. It is implemented in Python using the PyQt5 library.

## Features

- Open, edit, and save KTB files.
- Import and export data in JSON format.
- Search functionality to find specific entries in the table.
- Duplicate, add, and delete rows in the table.
- Drag and drop functionality to rearrange rows in the table.
- Display Unicode characters in the table with tooltips showing their decimal and hexadecimal values.
- Progress bar to show the progress of file loading.

## Classes

- `DraggableTableWidget`: A subclass of `QTableWidget` that allows rows to be dragged and dropped to rearrange them.
- `UnicodeTableWidgetItem`: A subclass of `QTableWidgetItem` that displays Unicode characters with tooltips showing their decimal and hexadecimal values.
- `FileLoader`: A subclass of `QThread` that loads a KTB file in a separate thread to avoid blocking the GUI.
- `KTBParserGUI`: The main class that implements the GUI.

## Usage

Run the `ktb_parser_gui.py` script to start the GUI. Use the menu bar to open a KTB file, save the current file, save the current file as a new file, import data from a JSON file, or export data to a JSON file. Use the search bar to find specific entries in the table. Use the buttons below the table to add or delete rows. You can also duplicate a row by selecting it and pressing Ctrl+D.

## Dependencies

- Python 3
- PyQt5