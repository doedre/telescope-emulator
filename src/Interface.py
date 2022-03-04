import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget
from PyQt5.QtWidgets import QGridLayout, QLabel, QMessageBox, QRadioButton
from PyQt5.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QComboBox
from PyQt5.QtGui import QPixmap

class Interface(QWidget):

    def __init__(self):
        super().__init__()
        QMainWindow.__init__(self)
        #self.setWindowIcon(QIcon("Icon.png"))
        self.setWindowTitle("TEI: Telescope Emulator Interface")
        self.setGeometry(300, 300, 1500, 1000)

        #Creating 2 tabs: iron for telescope, silver for error tests
        Tabs = QTabWidget()
        self.create_tab(Tabs, FirstTab(), "Telescope")
        #self.create_tab(Tabs, SecondTab(), "Errors scenarios")

        Layout = QGridLayout()
        self.setLayout(Layout)
        Layout.addWidget(Tabs, 0, 0)

    def create_tab(self, tabwidget, content, tab_name):
        tabwidget.addTab(content, tab_name)

class FirstTab(QWidget):

    def __init__(self):
        super().__init__()
        
        #Widget list: texts, fields, images, buttons etc.
        
        #Weather
        Text_weather = QLabel("Set weather conditions")
        self.Combo_weather = QComboBox()
        self.Combo_weather.addItems(["Perfect"," Good", "Bad"])
        #Object
        Text_object = QLabel("Set object coordinates in degree float d. format, or open file.\nFile may content more than one object")
        Text_RA = QLabel("Right Ascension")
        Text_Dec = QLabel("Declination")
        self.Field_RA = QLineEdit()
        self.Field_Dec = QLineEdit()
        self.Field_RA.setFixedWidth(300)
        self.Field_Dec.setFixedWidth(300)
        Button_object = QPushButton("Select objects")
        #Misc. parameters: exposure, slit orientation, frame type, calibration, guidance mode etc
        Text_exposure = QLabel("Set exposure time")
        self.Field_exposure = QLineEdit()
        self.Field_exposure.setFixedWidth(200)
        Text_slit = QLabel("Set slit orientation")
        self.Field_slit = QLineEdit()
        self.Field_slit.setFixedWidth(200)
        Button_park = QPushButton("Parking position")
        Button_start = QPushButton("Start observation")
        Button_move = QPushButton("Move telescope")
        Button_focus = QPushButton("Focus")
        Text_mode = QLabel("Set observation mode")
        Text_guide = QLabel("Set guidance mode")
        self.Combo_guide = QComboBox()
        self.Combo_guide.addItems(["A", "B"]) 
        self.Combo_mode = QComboBox()
        self.Combo_mode.addItems(["Imaging", "Spectrum"])
        Text_calibration = QLabel("Set calibration type if needed, otherwise set None")
        self.Combo_calibration = QComboBox()
        self.Combo_calibration.addItems(["None", "Calibration lamp", "Dark frame", "Flat field"])
        #Specially created shitwidget for taking place
        Void = QLabel("")
        Border = QLabel("")
        #Image
        #Frame = QPixmap("/home/evgeny/TEI/example.jpg")
        #FrameLbl = QLabel(self)
        #FrameLbl.setPixmap(Frame)
        #All important info about current task and the label to display it
        #Info = "Current task:\nObject: " + str(self.Field_RA.text()) + " ; " + str(self.Field_Dec.text()) + "\nTelescope mode: " + str(self.Combo_mode.currentText()) + "\nExposure time: " + str(self.Field_exposure.text())
        self.Current = QLabel()
        #self.Current.setFont(14)
        Button_start.clicked.connect(self.Click_start)
        Button_park.clicked.connect(self.Click_park)

        #Main outer layout
        Layout = QGridLayout()
        
        #Current task layout
        Task_layout = QGridLayout()
        Task_layout.addWidget(self.Current, 0, 0)
        #Layout for object data fields
        Obj_layout = QGridLayout()
        Obj_layout.addWidget(Text_object, 0, 0)
        Obj_layout.addWidget(Text_RA, 1, 0)
        Obj_layout.addWidget(self.Field_RA, 1, 1)
        Obj_layout.addWidget(Text_Dec, 2, 0)
        Obj_layout.addWidget(self.Field_Dec, 2, 1)
        Obj_layout.addWidget(Button_object, 3, 0, 1, 3)
        Obj_layout.addWidget(Void, 4, 0)
        #Layout for observation info fields
        Obs_layout = QGridLayout()
        Obs_layout.addWidget(Text_exposure, 0, 0)
        Obs_layout.addWidget(self.Field_exposure, 0, 1)
        Obs_layout.addWidget(Text_slit, 1, 0)
        Obs_layout.addWidget(self.Field_slit, 1, 1)
        Obs_layout.addWidget(Text_mode, 2, 0)
        Obs_layout.addWidget(self.Combo_mode, 2, 1)
        Obs_layout.addWidget(Text_guide, 3, 0)
        Obs_layout.addWidget(self.Combo_guide, 3, 1)
        Obs_layout.addWidget(Text_weather, 4, 0)
        Obs_layout.addWidget(self.Combo_weather, 4, 1)
        Obs_layout.addWidget(Text_calibration, 5, 0)
        Obs_layout.addWidget(self.Combo_calibration, 5, 1)
        Obs_layout.addWidget(Border, 0, 2)
        #Layout for buttons
        But_layout = QGridLayout()
        But_layout.addWidget(Button_start, 0, 0)
        But_layout.addWidget(Button_park, 1, 1)
        But_layout.addWidget(Button_move, 0, 1)
        But_layout.addWidget(Button_focus, 1, 0)
        #Merging layouts
        Layout.addLayout(Task_layout, 0, 0)
        Layout.addLayout(Obj_layout, 0, 1)
        Layout.addLayout(Obs_layout, 1, 0)
        Layout.addLayout(But_layout, 1, 1)
        self.setLayout(Layout)
        
    #Methods
    #Method for showing current task after clicking Start button. This method also might contain target frame pop-out process
    def Click_start(self):
       Info = "Current task:\nObject (float d.): " + str(self.Field_RA.text()) + " ; " + str(self.Field_Dec.text()) + "\nTelescope mode: " 
       Info += str(self.Combo_mode.currentText()) + "\nExposure time: " + str(self.Field_exposure.text()) + " sec " + "\nGuidance mode: " 
       Info += str(self.Combo_guide.currentText()) + "\nWeather conditions: " + str(self.Combo_weather.currentText())
       if str(self.Combo_calibration.currentText()) != "None":
           Info += "\nCalibration type: " + str(self.Combo_calibration.currentText())
       self.Current.setText(Info)

    def Click_park(self):
        Info = "Current task: Parking" + "\nGuidance mode: " + str(self.Combo_guide.currentText())
        self.Current.setText(Info)


### Main Application ###


app = QApplication(sys.argv)
main = Interface()
main.show()
sys.exit(app.exec())
