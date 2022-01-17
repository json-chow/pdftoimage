import sys
import os
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from converter import Converter


class MainWindow(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("PDF <--> Image")
        # Beginning of Main UI Code
        self.input_type_label = qtw.QLabel("Input Type")
        self.input_type_combo = qtw.QComboBox()
        self.input_type_combo.addItem("PDF")
        self.input_type_combo.addItem("Image")
        self.input_type_combo.setCurrentIndex(-1)
        self.output_type_label = qtw.QLabel("Output Type")
        self.output_type_combo = qtw.QComboBox()

        self.add_button = qtw.QPushButton("Add")
        self.remove_button = qtw.QPushButton("Remove")

        self.output_button = qtw.QPushButton("Output Folder:")
        self.output_location = qtw.QLineEdit()

        self.files_label = qtw.QLabel("Files:")
        self.files_list = qtw.QListWidget()
        self.up_button = qtw.QPushButton("Move Up")
        self.down_button = qtw.QPushButton("Move Down")

        self.convert_button = qtw.QPushButton("Convert")
        self.progress_bar = qtw.QProgressBar()
        self.progress_bar.setValue(0)

        self.status = qtw.QLabel("Hello")

        # Layouts
        main_layout = qtw.QVBoxLayout()
        self.setLayout(main_layout)
        # Show Input/Output Type Combo Boxes and Add/Remove Buttons
        types_addremove = qtw.QHBoxLayout()
        types = qtw.QFormLayout()
        types.setFormAlignment(qtc.Qt.AlignVCenter)
        types.addRow(self.input_type_label, self.input_type_combo)
        types.addRow(self.output_type_label, self.output_type_combo)
        types_addremove.addLayout(types)

        addremove = qtw.QVBoxLayout()
        addremove.addWidget(self.add_button)
        addremove.addWidget(self.remove_button)
        types_addremove.addLayout(addremove)
        
        main_layout.addLayout(types_addremove)

        # Show output folder button
        output = qtw.QHBoxLayout()
        output.addWidget(self.output_button)
        output.addWidget(self.output_location)

        main_layout.addLayout(output)

        # Show added files list
        main_layout.addWidget(self.files_label)
        files = qtw.QVBoxLayout()
        files.addWidget(self.files_list)
        
        up_down = qtw.QHBoxLayout()
        up_down.addWidget(self.up_button)
        up_down.addWidget(self.down_button)
        files.addLayout(up_down)

        main_layout.addLayout(files)

        # Show convert button and progress bar
        main_layout.addWidget(self.convert_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status)

        # End of Main UI Code
        self.show()

        # Initialize variables
        self.input_files = []
        self.input_type = ""
        self.output_folder = ""
        self.output_type = ""
        self.current_file_num = 0
        self.converting = False

        # Signals/Slots Connections Stuff
        self.input_type_combo.currentIndexChanged.connect(self.populate_output_combo)
        self.output_type_combo.currentTextChanged.connect(self.set_output_type)
        self.output_button.clicked.connect(self.set_output_folder)
        self.output_location.editingFinished.connect(self.set_output_folder_manual)
        self.add_button.clicked.connect(self.add_files)
        self.remove_button.clicked.connect(self.remove_files)
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        self.convert_button.clicked.connect(self.convert)

    @qtc.Slot(int)
    def populate_output_combo(self, index):
        '''Populates the output type combobox when an input type is selected'''
        self.input_files = []
        self.files_list.clear()
        self.progress_bar.setValue(0)
        self.input_type = index
        while self.output_type_combo.count() > 0:
            self.output_type_combo.removeItem(0)
        if index == 0: # If input is PDF
            self.filters = "PDF Files (*.pdf)" 
            self.output_type_combo.addItem("JPEG")
        elif index == 1: # If input is an Image
            self.filters = "Image Files (*.jpg *.jpeg *.png *.tiff *.bmp *.ico)"
            self.output_type_combo.addItem("PDF")
        self.output_type_combo.setCurrentIndex(-1)
        self.output_type = ""

    def set_output_type(self, text):
        '''Extracts the selected output type from the combobox'''
        self.output_type = text.lower()
    
    def set_output_folder(self):
        '''Extracts the selected output directory from the file dialog'''
        dialog = qtw.QFileDialog()
        self.output_folder = dialog.getExistingDirectory()
        self.output_location.setText(self.output_folder)

    def set_output_folder_manual(self):
        '''Extracts the specified output directory from changes in the line edit'''
        self.output_folder = self.output_location.text()
    
    def add_files(self):
        '''Adds files to an internal list and displays it'''
        if self.input_type_combo.currentIndex() != -1:
            dialog = qtw.QFileDialog()
            self.input_files_queue = dialog.getOpenFileNames(filter=self.filters)[0]
            self.files_list.addItems(self.input_files_queue)
            self.input_files = self.input_files + self.input_files_queue
        else:
            self.status.setText("Set the input file type.")

    def remove_files(self):
        '''Removes files from the internal list and removes it from display'''
        index = self.files_list.currentRow()
        if index != -1:
            self.files_list.takeItem(index)
            self.input_files.pop(index)
        else:
            self.status.setText("No files to remove.")

    def move_up(self):
        '''Moves the selected file up in the queue'''
        current_index = self.files_list.currentRow()
        if current_index != -1:
            swap_index = (current_index - 1) % self.files_list.count()
            current_item = self.files_list.item(current_index)
            self.files_list.takeItem(current_index)
            self.files_list.insertItem(swap_index, current_item)
            self.files_list.setCurrentRow(swap_index)
            self.input_files.insert(swap_index, self.input_files.pop(current_index))
        else:
            self.status.setText("No files to move up.")

    def move_down(self):
        '''Moves the selected file down in the queue'''
        current_index = self.files_list.currentRow()
        if current_index != -1:
            swap_index = (current_index + 1) % self.files_list.count()
            current_item = self.files_list.item(current_index)
            self.files_list.takeItem(current_index)
            self.files_list.insertItem(swap_index, current_item)
            self.files_list.setCurrentRow(swap_index)
            self.input_files.insert(swap_index, self.input_files.pop(current_index))
        else:
            self.status.setText("No files to move down.")
    
    def convert(self):
        if self.input_files and os.path.isdir(self.output_folder) and self.output_type and not self.converting:
            self.converting = True
            self.progress_bar.setValue(0)
            self.numFiles = len(self.input_files) # For progress bar
            # Creates a new thread
            self.convert_thread = qtc.QThread()
            # Creates a new converter object
            self.converter = Converter(self.input_type, self.output_type, self.input_files, self.output_folder)
            self.converter.progress_update.connect(self.update_progress)
            # Moves converter object to the new thread
            self.converter.moveToThread(self.convert_thread)
            self.convert_thread.started.connect(self.converter.run)
            self.convert_thread.start()
            self.status.setText("Converting...")
        else:
            if self.converting:
                self.status.setText("Already converting...")
            else:
                self.status.setText("Missing some fields or no inputs/output.")
    
    def update_progress(self):
        '''Updates the progress bar'''
        self.current_file_num += 1
        self.progress_bar.setValue(int((self.current_file_num / self.numFiles) * 100))

        if self.current_file_num == self.numFiles:
            self.current_file_num = 0
            self.convert_thread.exit()
            self.status.setText("Finished.")
            self.converting = False


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())