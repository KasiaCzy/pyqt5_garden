from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import date
import style


class ChangeDateWindow(QWidget):
    date_changed = pyqtSignal()

    def __init__(self, connection, cursor):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.setWindowTitle("Watering plant")
        self.setWindowIcon(QIcon("icons/watering.png"))
        self.setGeometry(250, 150, 400, 400)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        # top layout widgets
        self.text = QLabel("Watering")
        self.text.setAlignment(Qt.AlignCenter)
        self.image = QLabel()
        self.image.setPixmap(QPixmap('icons/watering.png'))
        self.image.setAlignment(Qt.AlignCenter)
        # bottom layout widgets
        self.plant_box = QComboBox()
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet(style.btn_style())
        self.submit_btn.clicked.connect(self.submit_changed_date)

        query_plants = "SELECT id,name FROM plants"
        plants = self.cursor.execute(query_plants).fetchall()

        for plant in plants:
            self.plant_box.addItem(plant[1], plant[0])

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.bottom_layout = QFormLayout()
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.tool_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.tool_bottom_frame())

        self.top_layout.addWidget(self.text)
        self.top_layout.addWidget(self.image)
        self.top_frame.setLayout(self.top_layout)

        self.bottom_layout.addRow(QLabel("Select plant: "), self.plant_box)
        self.bottom_layout.addRow("", self.submit_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame, 40)
        self.main_layout.addWidget(self.bottom_frame, 60)
        self.setLayout(self.main_layout)

    def submit_changed_date(self):
        dt = date.today().strftime("%d.%m.%Y")
        plant_id = self.plant_box.currentData()
        try:
            update_query = "UPDATE plants set watering_date=? WHERE id=?"
            self.cursor.execute(update_query, (dt, plant_id))
            self.connection.commit()
            QMessageBox.information(self, "Success", "Date of last watering has been update.")
            self.date_changed.emit()
        except:
            QMessageBox.information(self, "Warning", "Date of last watering has not been update.")