import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from PIL import Image
from datetime import timedelta
import style

con = sqlite3.connect("plants.db")
cur = con.cursor()

default_img = 'plant.png'


class AddPlant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add plant")
        self.setWindowIcon(QIcon("icons/icon.png"))
        self.setGeometry(250, 150, 500, 600)
        self.setFixedSize(self.size())
        self.UI()
        self.show()

    def UI(self):
        self.main_design()
        self.layouts()

    def main_design(self):
        # top layout widgets
        self.title = QLabel("Add plant")
        self.img = QLabel()
        self.img.setPixmap(QPixmap('icons/plant.png'))
        # bottom layout widgets
        # name field
        self.name_entry = QLineEdit()
        self.name_entry.setFont(QFont('', 10))
        self.name_entry.setPlaceholderText("Enter plant name")
        # watering_freq field
        self.watering_freq_box = QComboBox()
        self.watering_freq_box.setPlaceholderText("--Select--")
        self.watering_freq_box.addItems(['regularly', 'infrequently'])
        # note field
        self.note_entry = QTextEdit()
        self.note_entry.setPlaceholderText("Enter useful information")
        # last_watering field
        self.last_watering_entry = QDateEdit()
        self.last_watering_entry.setFont(QFont('', 10))
        self.last_watering_entry.setMinimumDate(QDate.currentDate().toPyDate() - timedelta(days=10))
        self.last_watering_entry.setCalendarPopup(True)
        # img field
        self.img_btn = QPushButton("Upload")
        self.img_btn.setStyleSheet(style.upload_btn_style())
        # buttons
        self.img_btn.clicked.connect(self.upload_img)
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet(style.btn_style())
        self.submit_btn.clicked.connect(self.add_plant)

    def layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.bottom_layout = QFormLayout()
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.tool_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.tool_bottom_frame())
        # adding widgets to layouts
        # top layout
        self.top_layout.addWidget(self.img)
        self.top_layout.addWidget(self.title)
        self.top_frame.setLayout(self.top_layout)
        # bottom layout
        self.bottom_layout.addRow(QLabel("Name: "), self.name_entry)
        self.bottom_layout.addRow(QLabel("Watering frequency: "), self.watering_freq_box)
        self.bottom_layout.addRow(QLabel("Last watering date: "), self.last_watering_entry)
        self.bottom_layout.addRow(QLabel("Image: "), self.img_btn)
        self.bottom_layout.addRow(QLabel("Note: "), self.note_entry)
        self.bottom_layout.addRow("", self.submit_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def upload_img(self):
        global default_img
        size = (128, 128)
        self.file_path,ok = QFileDialog.getOpenFileName(self, "Upload image", "", "Image Files(*.jpg *.png)")
        if ok:
            default_img = os.path.basename(self.file_path)
            img = Image.open(self.file_path).resize(size)
            img.save(f'images/{default_img}')

    def add_plant(self):
        global default_img
        name = self.name_entry.text()
        watering_freq = self.watering_freq_box.currentText()
        note = self.note_entry.toPlainText()
        last_watering = self.last_watering_entry.text()
        img = default_img

        if name and last_watering and watering_freq:
            try:
                query = "INSERT INTO plants (name,watering_frequency,watering_date,note,img) VALUES(?,?,?,?,?)"
                cur.execute(query,(name, watering_freq, last_watering, note, img))
                con.commit()
                QMessageBox.information(self, "Success", "Plant has been added.")
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Plant has not been added.")
        else:
            QMessageBox.information(self, "Warning", 'Fields: "Name", "Last watering date" '
                                                     'and "Watering frequency" can not be empty.')