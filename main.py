import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from PIL import Image
from datetime import timedelta, datetime, date
import addPlant, style, changeDate

con = sqlite3.connect("plants.db")
cur = con.cursor()

plant_id = None
default_img = 'plant.png'


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Home Garden")
        self.setWindowIcon(QIcon("icons/icon.png"))
        self.setGeometry(250, 150, 1350, 850)
        self.setFixedSize(self.size())

        self.UI()
        self.show()

    def UI(self):
        self.tool_bar()
        self.tab_widget()
        self.widgets()
        self.layouts()
        self.display_plants()
        self.display_watering_list()

    def tool_bar(self):
        self.tb = self.addToolBar("Tool Bar")
        self.tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # Buttons
        # add plant
        self.add_plant = QAction(QIcon("icons/add.png"), "Add plant", self)
        self.tb.addAction(self.add_plant)
        self.add_plant.triggered.connect(self.add_new_plant)
        self.tb.addSeparator()
        # watering button
        self.watering = QAction(QIcon("icons/watering.png"), "Watering plant", self)
        self.tb.addAction(self.watering)
        self.watering.triggered.connect(self.change_last_watering_date)
        self.tb.addSeparator()

    def tab_widget(self):
        self.tabs = QTabWidget()
        self.tabs.blockSignals(True)
        self.tabs.currentChanged.connect(self.refresh_tabs_view)
        self.setCentralWidget(self.tabs)
        self.tab_home_paige = QWidget()
        self.tab_plants_list = QWidget()
        self.tab_watering_list = QWidget()
        self.tabs.addTab(self.tab_home_paige, QIcon("icons/icon.png"), "Home Garden")
        self.tabs.addTab(self.tab_plants_list, QIcon("icons/plants.png"), "List of plants")
        self.tabs.addTab(self.tab_watering_list, QIcon("icons/plant.png"), "List for today")

    def widgets(self):
        # home_paige tab widgets
        self.home_title = QLabel("It's time to care for your houseplants!\n\n"
                                 "Watering your plants is key to keeping them healthy. But remember one rule:\n"
                                 "Water the plants only as often as needed.\n"
                                 "Before you water you should check how dry the soil is.")
        self.home_title.setAlignment(Qt.AlignCenter)
        self.home_text = QLabel("""# Create list of your houseplants.
        
        # Always update date of last watering.
        
        # Check daily watering reminders list to keep your plants well.""")
        self.home_text.setAlignment(Qt.AlignCenter)
        # tab_plants_list widgets
        # plant table widget
        self.plants_table = QTableWidget()
        self.plants_table.setColumnCount(4)
        self.plants_table.setColumnHidden(0, True)
        self.plants_table.setHorizontalHeaderItem(0, QTableWidgetItem("Id"))
        self.plants_table.setHorizontalHeaderItem(1, QTableWidgetItem("Name"))
        self.plants_table.setHorizontalHeaderItem(2, QTableWidgetItem("Watering frequency"))
        self.plants_table.setHorizontalHeaderItem(3, QTableWidgetItem("Date of last watering"))
        self.plants_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.plants_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.plants_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.plants_table.doubleClicked.connect(self.display_selected_plant)
        self.plants_table.itemClicked.connect(self.display_single_click_plant_table)
        # right top layout widget
        self.plants_search_text = QLabel("Search")
        self.plants_search_entry = QLineEdit()
        self.plants_search_entry.setPlaceholderText("Search for plant")
        self.plants_search_button = QPushButton("Search")
        self.plants_search_button.setStyleSheet(style.btn_style())
        self.plants_search_button.clicked.connect(self.search_plant)
        # right middle layout widget
        self.all_plants = QRadioButton("All plants")
        self.watering_freq_regularly = QRadioButton("Watering regularly")
        self.watering_freq_infrequently = QRadioButton("Watering infrequently")
        self.plants_list_button = QPushButton("Search")
        self.plants_list_button.setStyleSheet(style.btn_style())
        self.plants_list_button.clicked.connect(self.filter_plants_tabel)
        # tab_watering_list widgets
        # list table widget
        self.list_table = QTableWidget()
        self.list_table.setColumnCount(4)
        self.list_table.setColumnHidden(0, True)
        self.list_table.setHorizontalHeaderItem(0, QTableWidgetItem("Id"))
        self.list_table.setHorizontalHeaderItem(1, QTableWidgetItem("Name"))
        self.list_table.setHorizontalHeaderItem(2, QTableWidgetItem("Watering frequency"))
        self.list_table.setHorizontalHeaderItem(3, QTableWidgetItem("Date of last watering"))
        self.list_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.list_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.list_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.list_table.itemClicked.connect(self.display_single_click_list_table)
        # right layout widget
        self.watering_all_btn = QPushButton("Watering All")
        self.watering_all_btn.setStyleSheet(style.upload_btn_style())
        self.watering_all_btn.clicked.connect(self.water_all_plants)


    def layouts(self):
        # tab_index layouts
        self.home_main_layout = QVBoxLayout()
        self.home_top_layout = QHBoxLayout()
        self.home_bottom_layout = QHBoxLayout()
        self.home_top_frame = QFrame()
        self.home_top_frame.setStyleSheet(style.home_top_frame())
        self.home_bottom_frame = QFrame()
        self.home_bottom_frame.setStyleSheet(style.home_bottom_frame())
        self.home_top_layout.addWidget(self.home_title)
        self.home_top_frame.setLayout(self.home_top_layout)
        self.home_bottom_layout.addWidget(self.home_text)
        self.home_bottom_frame.setLayout(self.home_bottom_layout)
        self.home_main_layout.addWidget(self.home_top_frame)
        self.home_main_layout.addWidget(self.home_bottom_frame)

        self.tab_home_paige.setLayout(self.home_main_layout)
        # tab_plants_list layouts
        self.plants_main_layout = QHBoxLayout()
        self.plants_main_left_layout = QVBoxLayout()
        self.plants_main_right_layout = QVBoxLayout()
        self.plants_right_top_layout = QHBoxLayout()
        self.plants_right_middle_layout = QHBoxLayout()
        self.plants_right_bottom_layout = QFormLayout()
        self.plants_top_group_box = QGroupBox("Search Box")
        self.plants_top_group_box.setStyleSheet(style.search_box_style())
        self.plants_middle_group_box = QGroupBox("List Box")
        self.plants_middle_group_box.setStyleSheet(style.list_box_style())
        self.plants_bottom_group_box = QFrame()
        self.plants_bottom_group_box.setStyleSheet(style.plant_view())
        self.plants_bottom_group_box.setLayout(self.plants_right_bottom_layout)
        # add widgets
        self.plants_main_left_layout.addWidget(self.plants_table)

        self.plants_right_top_layout.addWidget(self.plants_search_text)
        self.plants_right_top_layout.addWidget(self.plants_search_entry)
        self.plants_right_top_layout.addWidget(self.plants_search_button)
        self.plants_top_group_box.setLayout(self.plants_right_top_layout)

        self.plants_right_middle_layout.addWidget(self.all_plants)
        self.plants_right_middle_layout.addWidget(self.watering_freq_regularly)
        self.plants_right_middle_layout.addWidget(self.watering_freq_infrequently)
        self.plants_right_middle_layout.addWidget(self.plants_list_button)
        self.plants_middle_group_box.setLayout(self.plants_right_middle_layout)
        # add layouts
        self.plants_main_layout.addLayout(self.plants_main_left_layout, 60)
        self.plants_main_layout.addLayout(self.plants_main_right_layout, 40)
        self.plants_main_right_layout.addWidget(self.plants_top_group_box, 20)
        self.plants_main_right_layout.addWidget(self.plants_middle_group_box, 20)
        self.plants_main_right_layout.addWidget(self.plants_bottom_group_box, 60)
        self.tab_plants_list.setLayout(self.plants_main_layout)
        # tab_list_for_today layouts
        self.list_main_layout = QHBoxLayout()
        self.list_main_left_layout = QVBoxLayout()
        self.list_main_right_layout = QVBoxLayout()
        self.list_right_top_layout = QHBoxLayout()
        self.list_right_top_layout.setContentsMargins(0, 20, 0, 100)
        self.list_right_bottom_layout = QFormLayout()
        self.list_bottom_frame = QFrame()
        self.list_bottom_frame.setStyleSheet(style.plant_view())
        # add widgets
        self.list_main_left_layout.addWidget(self.list_table)
        self.list_right_top_layout.addWidget(self.watering_all_btn)
        self.list_bottom_frame.setLayout(self.list_right_bottom_layout)
        self.list_main_right_layout.addLayout(self.list_right_top_layout)
        self.list_main_right_layout.addWidget(self.list_bottom_frame)
        self.list_main_layout.addLayout(self.list_main_left_layout, 60)
        self.list_main_layout.addLayout(self.list_main_right_layout, 40)
        self.tab_watering_list.setLayout(self.list_main_layout)

        self.tabs.blockSignals(False)

    def add_new_plant(self):
        self.new_plant_window = addPlant.AddPlant()

    def change_last_watering_date(self):
        self.watering_plant_window = changeDate.ChangeDate()

    def display_plants(self):
        self.plants_table.setFont(QFont("Arial", 12))
        for i in reversed(range(self.plants_table.rowCount())):
            self.plants_table.removeRow(i)

        query = cur.execute("SELECT id,name,watering_frequency,watering_date FROM plants")
        for row_data in query:
            row_number = self.plants_table.rowCount()
            self.plants_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.plants_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.plants_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def display_watering_list(self):
        date = datetime.now()
        self.list_table.setFont(QFont("Arial", 12))
        for i in reversed(range(self.list_table.rowCount())):
            self.list_table.removeRow(i)
        query = cur.execute("SELECT id,name,watering_frequency,watering_date FROM plants")
        for plant in query:
            if plant[2] == 'regularly':
                if datetime.strptime(plant[3], "%d.%m.%Y") + timedelta(days=5) <= date:
                    row_number = self.list_table.rowCount()
                    self.list_table.insertRow(row_number)
                    for column_number, data in enumerate(plant):
                        self.list_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
            else:
                if datetime.strptime(plant[3], "%d.%m.%Y") + timedelta(days=10) <= date:
                    row_number = self.list_table.rowCount()
                    self.list_table.insertRow(row_number)
                    for column_number, data in enumerate(plant):
                        self.list_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.plants_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def display_selected_plant(self):
        global plant_id
        list_plant = []
        for i in range(0, 4):
            list_plant.append(self.plants_table.item(self.plants_table.currentRow(), i).text())
        plant_id = list_plant[0]
        self.display_window = DisplayPlant()

    def display_single_click_plant_table(self):
        item_id = self.plants_table.item(self.plants_table.currentRow(), 0).text()
        # plants_right_bottom_layout
        for i in reversed(range(self.plants_right_bottom_layout.count())):
            widget = self.plants_right_bottom_layout.takeAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        query = "SELECT * FROM plants WHERE id=?"
        selected_plant = cur.execute(query, (item_id,)).fetchone()
        img = QLabel()
        img.setPixmap(QPixmap(f'images/{selected_plant[5]}'))
        name = QLabel(selected_plant[1])
        watering_date = QLabel(selected_plant[3])
        watering_freq = QLabel(selected_plant[2])
        note = QLabel(selected_plant[4])
        self.plants_right_bottom_layout.setVerticalSpacing(20)
        self.plants_right_bottom_layout.addRow(img)
        self.plants_right_bottom_layout.addRow("Name: ", name)
        self.plants_right_bottom_layout.addRow("Date of last watering: ", watering_date)
        self.plants_right_bottom_layout.addRow("Watering frequency: ", watering_freq)
        self.plants_right_bottom_layout.addRow("Note: ", note)

    def display_single_click_list_table(self):
        item_id = self.list_table.item(self.list_table.currentRow(), 0).text()
        # plants_right_bottom_layout
        for i in reversed(range(self.list_right_bottom_layout.count())):
            widget = self.list_right_bottom_layout.takeAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        query = "SELECT * FROM plants WHERE id=?"
        selected_plant = cur.execute(query, (item_id,)).fetchone()
        img = QLabel()
        img.setPixmap(QPixmap(f'images/{selected_plant[5]}'))
        name = QLabel(selected_plant[1])
        watering_date = QLabel(selected_plant[3])
        watering_freq = QLabel(selected_plant[2])
        note = QLabel(selected_plant[4])
        self.list_right_bottom_layout.setVerticalSpacing(20)
        self.list_right_bottom_layout.addRow(img)
        self.list_right_bottom_layout.addRow("Name: ", name)
        self.list_right_bottom_layout.addRow("Date of last watering: ", watering_date)
        self.list_right_bottom_layout.addRow("Watering frequency: ", watering_freq)
        self.list_right_bottom_layout.addRow("Note: ", note)

    def search_plant(self):
        value = self.plants_search_entry.text()
        if not value:
            QMessageBox.information(self, "Warning", "Search field can not be empty.")
        else:
            self.plants_search_entry.setText("")
            query = "SELECT id,name,watering_frequency,watering_date FROM plants WHERE name LIKE ?"
            results = cur.execute(query, (f'%{value}%',)).fetchall()
            if len(results) == 0:
                QMessageBox.information(self, "Warning", "Not found.")
            else:
                for i in reversed(range(self.plants_table.rowCount())):
                    self.plants_table.removeRow(i)
                for row_data in results:
                    row_number = self.plants_table.rowCount()
                    self.plants_table.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        self.plants_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def filter_plants_tabel(self):
        if self.all_plants.isChecked():
            self.display_plants()
        elif self.watering_freq_regularly.isChecked():
            query = "SELECT id,name,watering_frequency,watering_date FROM plants WHERE watering_frequency='regularly'"
            plants = cur.execute(query).fetchall()
            for i in reversed(range(self.plants_table.rowCount())):
                self.plants_table.removeRow(i)
            for row_data in plants:
                row_number = self.plants_table.rowCount()
                self.plants_table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.plants_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        elif self.watering_freq_infrequently.isChecked():
            query = "SELECT id,name,watering_frequency,watering_date FROM plants " \
                    "WHERE watering_frequency='infrequently'"
            plants = cur.execute(query).fetchall()
            for i in reversed(range(self.plants_table.rowCount())):
                self.plants_table.removeRow(i)
            for row_data in plants:
                row_number = self.plants_table.rowCount()
                self.plants_table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.plants_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def water_all_plants(self):
        dt = date.today().strftime("%d.%m.%Y")
        success = None
        counter = self.list_table.rowCount()
        for row in range(0, counter):
            try:
                id_number = self.list_table.takeItem(row, 0).text()
                print(id_number)
                update_query = "UPDATE plants set watering_date=? WHERE id=?"
                cur.execute(update_query, (dt, id_number))
                con.commit()
                success = True
            except:
                success = False
        if success:
            QMessageBox.information(self, "Success", "Date of last watering has been update.")
        else:
            QMessageBox.information(self, "Warning", "Date of last watering has not been update.")

    def refresh_tabs_view(self):
        self.display_plants()
        self.display_watering_list()


class DisplayPlant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Plant")
        self.setWindowIcon(QIcon("icons/icon.png"))
        self.setGeometry(250, 150, 500, 600)
        self.setFixedSize(self.size())
        self.UI()
        self.show()

    def UI(self):
        self.prepare_plant_details()
        self.widgets()
        self.layouts()

    def prepare_plant_details(self):
        global plant_id
        query = "SELECT * FROM plants WHERE id=?"
        plant = cur.execute(query, (plant_id,)).fetchone()
        self.plant_name = plant[1]
        self.watering_freq = plant[2]
        self.watering_date = plant[3]
        self.plant_note = plant[4]
        self.plant_img = plant[5]

    def widgets(self):
        # top layouts widgets
        self.plant_image = QLabel()
        self.plant_image.setPixmap(QPixmap(f'images/{self.plant_img}'))
        self.plant_image.setAlignment(Qt.AlignCenter)
        self.plant_name_text = QLabel(f'{self.plant_name}')
        self.plant_name_text.setAlignment(Qt.AlignCenter)
        # bottom layouts widgets
        self.plant_name_entry = QLineEdit()
        self.plant_name_entry.setFont(QFont('', 10))
        self.plant_name_entry.setText(self.plant_name)
        self.watering_freq_box = QComboBox()
        self.watering_freq_box.setFont(QFont('', 10))
        self.watering_freq_box.addItems(['regularly', 'infrequently'])
        index = self.watering_freq_box.findText(self.watering_freq, Qt.MatchFixedString)
        self.watering_freq_box.setCurrentIndex(index)
        self.watering_date_entry = QDateEdit()
        self.watering_date_entry.setFont(QFont('', 10))
        dt = datetime.strptime(self.watering_date, "%d.%m.%Y")
        self.watering_date_entry.setMinimumDate(dt)
        self.watering_date_entry.setCalendarPopup(True)
        self.plant_note_entry = QTextEdit()
        self.plant_note_entry.setText(self.plant_note)

        self.img_btn = QPushButton("Upload")
        self.img_btn.setStyleSheet(style.upload_btn_style())
        self.img_btn.clicked.connect(self.upload_image)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(style.delete_btn_style())
        self.delete_btn.clicked.connect(self.delete_plant)
        self.update_btn = QPushButton("Update")
        self.update_btn.setStyleSheet(style.btn_style())
        self.update_btn.clicked.connect(self.update_plant)

    def layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.bottom_layout = QFormLayout()
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.tool_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.tool_bottom_frame())
        # top layout
        self.top_layout.addWidget(self.plant_name_text)
        self.top_layout.addWidget(self.plant_image)
        self.top_frame.setLayout(self.top_layout)
        # bottom layout
        self.bottom_layout.addRow(QLabel("Name: "), self.plant_name_entry)
        self.bottom_layout.addRow(QLabel("Watering frequency: "), self.watering_freq_box)
        self.bottom_layout.addRow(QLabel("Last watering date: "), self.watering_date_entry)
        self.bottom_layout.addRow(QLabel("Note: "), self.plant_note_entry)
        self.bottom_layout.addRow(QLabel("Image: "), self.img_btn)
        self.bottom_layout.addRow("", self.delete_btn)
        self.bottom_layout.addRow("", self.update_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def upload_image(self):
        global default_img
        size = (128, 128)
        self.file_path, ok = QFileDialog.getOpenFileName(self, "Upload image", "", "Image Files(*.jpg *.png)")
        if ok:
            default_img = os.path.basename(self.file_path)
            img = Image.open(self.file_path).resize(size)
            img.save(f'images/{default_img}')

    def update_plant(self):
        global plant_id
        name = self.plant_name_entry.text()
        watering_freq = self.watering_freq_box.currentText()
        note = self.plant_note_entry.toPlainText()
        last_watering = self.watering_date_entry.text()
        img = self.plant_img

        if name and last_watering and watering_freq:
            try:
                query = "UPDATE plants set name=?, watering_frequency=?, watering_date=?, note=?, img=? WHERE id=?"
                cur.execute(query,(name, watering_freq, last_watering, note, img, plant_id))
                con.commit()
                QMessageBox.information(self, "Success", "Plant has been update.")
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Plant has not been update.")
        else:
            QMessageBox.information(self, "Warning", 'Fields: "Name", "Last watering date" '
                                                     'and "Watering frequency" can not be empty.')

    def delete_plant(self):
        global plant_id
        mbox = QMessageBox.question(self, "Warning", "Are you sure to delete this plant?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if mbox == QMessageBox.Yes:
            try:
                query = "DELETE FROM plants WHERE id=?"
                cur.execute(query, (plant_id,))
                con.commit()
                QMessageBox.information(self, "Information", "Plant has been deleted")
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Plant has not been deleted")


def main():
    app = QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
