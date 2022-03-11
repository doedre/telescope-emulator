import sys
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget
from PySide6.QtWidgets import QGridLayout, QLabel, QMessageBox, QRadioButton
from PySide6.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QComboBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QPixmap
from numpy import loadtxt

import te_fits as tft

class Interface(QWidget):

    moveButtonClicked = Signal(float, float)
    parkButtonClicked = Signal()
    startButtonClicked = Signal(str)
    telescopeMoved = Signal(float, float)

    def __init__(self):
        super().__init__()
        #self.setWindowIcon(QIcon("Icon.png"))
        self.setWindowTitle("TEI: Telescope Emulator Interface")
        self.setGeometry(300, 300, 1500, 1000)

        #Creating 2 tabs: iron for telescope, silver for error tests
        Tabs = QTabWidget()
        tabs = FirstTab()
        self.create_tab(Tabs, tabs, "Telescope")
        tabs.moveButtonClicked.connect(self.moveButtonClicked)
        tabs.parkButtonClicked.connect(self.parkButtonClicked)
        tabs.startButtonClicked.connect(self.startButtonClicked)
        self.telescopeMoved.connect(tabs.telescopeMoved)
        self.create_tab(Tabs, tft.Plot_image("data/obj_image.fts"), "Guiding")

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
        self.Combo_weather.addItems(["Normal", "Good", "Bad"])
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
        
        #Image part, for now disabled
        #Frame = QPixmap("/home/evgeny/TEI/example.jpg")
        #FrameLbl = QLabel(self)
        #FrameLbl.setPixmap(Frame)
        
        #All important info about current task and the label to display it
        self.Current = QLabel()
        

        #Logic part. Button functions, vaulue retrieving methods etc
        self.Focus = False
        Button_start.clicked.connect(self.Click_start)
        Button_park.clicked.connect(self.Click_park)
        Button_focus.clicked.connect(self.Click_focus)
        Button_move.clicked.connect(self.Click_move)
        Button_object.clicked.connect(self.Open_file)


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

    moveButtonClicked = Signal(float, float)
    parkButtonClicked = Signal()
    startButtonClicked = Signal(str)
    
    @Slot(float, float)
    def telescopeMoved(self, alt: float, az: float):
        self.Current.setText("alt {0}, az {1}".format(alt, az))

    #Methods
    #Methods for showing current task after clicking buttons. These methods also might contain target frame pop-out processes
    def Click_start(self):
       Info = "Current task:\nObject (float d.): " + str(self.Field_RA.text()) + " ; " + str(self.Field_Dec.text()) + "\nTelescope mode: " 
       Info += str(self.Combo_mode.currentText()) + "\nExposure time: " + str(self.Field_exposure.text()) + " sec " + "\nGuidance mode: " 
       Info += str(self.Combo_guide.currentText()) + "\nWeather conditions: " + str(self.Combo_weather.currentText())
       if str(self.Combo_calibration.currentText()) != "None":
           Info += "\nCalibration type: " + str(self.Combo_calibration.currentText())
       self.Current.setText(Info)
       self.startButtonClicked.emit("data/obj_image.fts")

    def Click_park(self):
        Info = "Current task: Parking" + "\nGuidance mode: " + str(self.Combo_guide.currentText())
        self.Current.setText(Info)
        self.parkButtonClicked.emit()

    def Click_focus(self):
        Info = "Current task:\nFocusing"
        self.Current.setText(Info)
        self.Focus = True

    def Click_move(self):
        Info = "Current task:\nMoving to coordinates " + str(self.Field_RA.text()) + " ; " + str(self.Field_Dec.text())
        #Need current telescope coordinates. Add them here
        #Info += "Current coordinates: " + 
        self.Current.setText(Info)
        self.moveButtonClicked.emit(float(self.Field_RA.text()), float(self.Field_Dec.text()))

    def Get_focus(self):
        return self.Focus

    def Get_weather(self):
        weather = self.Combo_weather.currentText()
        head_weather = " "
        if weather == "Normal":
            head_weather = "normal"
        if weather == "Good":
            head_weather = "good"
        if weather == "Bad":
            head_weather = "bad"
        return head_weather

    def Get_filename(self):
        mode = " "
        file_type = " "
        if str(self.Combo_mode.currentText()) == "Imaging":
            mode = "image"
        if str(self.Combo_mode.currentText()) == "Spectrum":
            mode = "spectra"
        if str(self.Combo_calibration.currentText()) == "None":
            file_type = "obj"
        if str(self.Combo_calibration.currentText()) == "Calibration lamp":
            file_type = "neon"
        if str(self.Combo_calibration.currentText()) == "Flat field":
            file_type = "flat"

        return [mode, file_type]

    def Open_file(self):
        filepath = QFileDialog.getOpenFileName(self, "Open file")[0]
        data_RA, data_Dec = loadtxt(filepath, usecols = (0, 1), unpack = True)
        self.Field_RA.setText(str(data_RA[0]))
        self.Field_Dec.setText(str(data_Dec[0]))
