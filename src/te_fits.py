from PySide6.QtCore import QObject, Signal, Slot, QSize
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget
from PySide6.QtWidgets import QGridLayout, QLabel, QMessageBox, QRadioButton
from PySide6.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QComboBox
from PySide6.QtWidgets import QFileDialog, QCheckBox, QSplitter
from PySide6.QtGui import QPixmap, QFont


import matplotlib.patches as patches
import sys
import numpy as np
from threading import Lock
from astropy.io import fits
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import LogNorm

from datetime import datetime
import time
import te_coords
import logger as log

class Plot_image(QMainWindow):
    def __init__(self, filename):
        super().__init__()
        
        # Параметры (передаются извне, как - не знаю)
        self.name_fits=filename # Название файла
        #------

        # Размер окна
        self.setFixedSize(QSize(900, 1000))

        # Считывание из файла
        self.read_fits()
        self.setWindowTitle(self.h['OBJECT']) # название окна

        # Основное изображение
        self.figure = Figure(figsize=(7, 7))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self) # Панель инструментов
        self.image()
        
        # Вывод координат        
        self.label = QLabel()
        self.label.setFont(QFont('Arial', 10))

        # Отображение положения щели
        self.checkbox=QCheckBox('Slit')
        self.checkbox.setFont(QFont('Arial', 10))
        self.checkbox.stateChanged.connect(self.plot_slit)

        # Изменение цветовой схемы
        self.label2 = QLabel('Min value') 
        self.label2.setFont(QFont('Arial', 10))
        self.input1 = QLineEdit()
        self.input1.textChanged.connect(self.min_max_value)
        self.label3 = QLabel('Max value')
        self.label3.setFont(QFont('Arial', 10))
        self.input2 = QLineEdit()
        self.input2.textChanged.connect(self.min_max_value)
        self.checkbox2=QCheckBox('Log norm color')
        self.checkbox2.setFont(QFont('Arial', 10))
        self.checkbox2.stateChanged.connect(self.color_norm)
        
        # Дополнительное изображение (срез)
        self.figure2 = Figure(figsize=(7, 3))
        self.canvas2 = FigureCanvas(self.figure2)
        self.ax2 = self.figure2.subplots()
        self.canvas2.draw()
        
        # Вывод на экран
        layout = QVBoxLayout()
        splitter = QSplitter()
        splitter2 = QSplitter()
        layout.addWidget(self.toolbar) # Панель инструментов
        layout.addWidget(self.canvas) # Основное изображение
        if self.h['MODE']=='Image': # Отображение щели
            splitter.addWidget(self.checkbox)
        splitter.addWidget(self.label) # Координаты
        layout.addWidget(splitter)       
        splitter2.addWidget(self.checkbox2) # Логарифмическая цветовая схема
        splitter2.addWidget(self.label2) # Минимальное значение
        splitter2.addWidget(self.input1)
        splitter2.addWidget(self.label3) # Максимальное значение
        splitter2.addWidget(self.input2)        
        layout.addWidget(splitter2) 
        layout.addWidget(self.canvas2) # Дополнительное изображение
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)       

    # Считывание данных из файла
    def read_fits(self):
        # Считывание данных
        hdu = fits.open(self.name_fits)[0]
        self.h=hdu.header # Шапка
        self.Z=np.array(hdu.data) # Отсчеты пикселей
        
        # Начальные значения параметров изображения
        self.min_v=None 
        self.max_v=None
        self.norm_color=None
        if self.h['MODE']=='Image': # для разных типов изображения разные цветовые схемы
            self.color='gray'
        else:
            self.color='Greys'
            
        # Параметры щели
        self.state_slit=0 # Отображение
        self.height=len(self.Z) # Высота щели в Pix
        # Для вычисления ширины щели
        width_slit=float(self.h['SLITWID']) # ширина щели в "
        scale=self.h['IMSCALE'] # масштаб по оси x в "/Pix
        n=scale.index('x')
        scale=float(scale[0:n]) #
        #
        self.width=width_slit/scale # Ширина щели в Pix

    # Построение основного изображения
    def image(self):
        self.figure.clear()
        self.ax = self.figure.subplots()
        self.ax.set_axis_on()
        self.ax.format_coord = self.format_coord
        if self.state_slit==2: # Для отображения щели
            x_c=len(self.Z[0])/2 
            y_c=len(self.Z)/2
            x=x_c-self.width/2
            y=y_c-self.height/2
            rect = patches.Rectangle((x,y),self.width,self.height,angle=0, linewidth=1,edgecolor="g", facecolor="none")
            self.ax.add_patch(rect)
        im=self.ax.imshow(self.Z,cmap=self.color, vmin=self.min_v, vmax=self.max_v,norm=self.norm_color, origin='lower')
        cb=self.figure.colorbar(im,ax=self.ax)
        self.ax.set_xlabel("x, Pix")
        self.ax.set_ylabel("y, Pix")
        self.canvas.draw()

    # Отображение щели
    def plot_slit(self, state):
        if state==2:
            self.state_slit=2
        else:
            self.state_slit=0
        self.image()

    # Построение среза изображения (параллельно оси x)
    def graf(self,j):
        self.ax2.cla()
        self.X=[]
        self.Y=[]
        for i in range(len(self.Z[j])):
            self.X.append(i)
            self.Y.append(self.Z[j][i])
        self.ax2.plot(self.X,self.Y,'k')
        self.ax2.set_ylabel("value")
        self.canvas2.draw()
        
    # Отображение координат на рисунке
    def format_coord(self,x, y):
        numrows, numcols = self.Z.shape
        col = int(x+0.5) # x
        row = int(y+0.5) # y
        self.label.setText('x = '+str(col)+', y = '+str(row)+', value = '+str(self.Z[row][col]))
        self.graf(row)
        if col>=0 and col<numcols and row>=0 and row<numrows:
            z = self.Z[row][col]
            return 'x=%1.0f, y=%1.0f, z=%1.0f'%(x, y, z)
        else:
            return 'x=%1.0f, y=%1.0f'%(x, y)  

    # Цветовая схема
    def min_max_value(self):
        min_v=self.input1.text()
        max_v=self.input2.text()
        if min_v=='':
            self.min_v=None
        else:
            if max_v!='':
                if float(min_v)<float(max_v):
                    self.min_v=float(min_v)
                else:
                    self.min_v=None
            else:
                self.min_v=float(min_v)               
        if max_v=='':
            self.max_v=None  
        else:
            if min_v!='':
                if float(max_v)>float(min_v):
                    self.max_v=float(max_v)
                else:
                    self.max_v=None
            else:
                self.max_v=float(max_v)
        self.image()

    def color_norm(self, state):
        if state==2:
            self.norm_color=LogNorm()
        else:
            self.norm_color=None
        self.image()

def get_weather(weather, focus): # берём информацию о погоде и сиинге в зависимости от условий и наличия автофокуса
    file = np.genfromtxt('weather.txt', skip_header=1)
    if focus==False:
        if weather=='bad':
            mirrtemp = file[0, 1]
            dometemp = file[0, 2]
            outtemp = file[0, 3]
            wind = file[0, 4]
            clouds = file [0, 5]
            pressure = file [0, 6]
            seeing = file [0, 7]
        elif weather=='good':
            mirrtemp = file[2, 1]
            dometemp = file[2, 2]
            outtemp = file[2, 3]
            wind = file[2, 4]
            clouds = file [2, 5]
            pressure = file [2, 6]
            seeing = file [2, 7]
        elif weather=='normal':
            mirrtemp = file[4, 1]
            dometemp = file[4, 2]
            outtemp = file[4, 3]
            wind = file[4, 4]
            clouds = file [4, 5]
            pressure = file [4, 6]
            seeing = file [4, 7]
    if focus==True:
        if weather=='bad':
            mirrtemp = file[1, 1]
            dometemp = file[1, 2]
            outtemp = file[1, 3]
            wind = file[1, 4]
            clouds = file [1, 5]
            pressure = file [1, 6]
            seeing = file [1, 7]
        elif weather=='good':
            mirrtemp = file[3, 1]
            dometemp = file[3, 2]
            outtemp = file[3, 3]
            wind = file[3, 4]
            clouds = file [3, 5]
            pressure = file [3, 6]
            seeing = file [3, 7]
        elif weather=='normal':
            mirrtemp = file[5, 1]
            dometemp = file[5, 2]
            outtemp = file[5, 3]
            wind = file[5, 4]
            clouds = file [5, 5]
            pressure = file [5, 6]
            seeing = file [5, 7]
    return mirrtemp, dometemp, outtemp, wind, clouds, pressure, seeing 

# считывание fits-файла, возвращает отдельно данные (которые потом нужно переделать под экспозицию) и header
def read_fits(mode, file_type, exp_time):
    name = "./data/" + file_type + "_" + mode + '.fts'
    hdu = fits.open(name)
    image_data = hdu[0].data
    hdr = hdu[0].header
    time.sleep(exp_time*0.01)
    return image_data, hdr

def change_fits_with_exposition(image_data, exp_time): #меняем fits под экспозицию
    tau = exp_time 
    image_data = image_data/900
    image_data = image_data*tau
    image_data[np.where(data>20000)] = 200000

    return image_data

# запись нового fits-файла
# star - объект класса Star
# sid_time считается в main
# image_data - из change_fits_with_exposition, header - из read_fits
def write_fits(countfile, image_data, hdr, path, file_type, exp_time, star, sid_time, slit, weather, mode, focus):
    current_datetime = datetime.now()
    name = 's' + countfile + '.fts'
    mirrtemp, dometemp, outtemp, wind, clouds, pressure, seeing = get_weather(weather, focus)
    hdu = fits.PrimaryHDU(data = image_data)
    hdu.header = hdr
    hdu.header['DATE'] = '\'' + current_datetime.date() + '\''
    hdu.header['DATE-OBS'] = '\'' + current_datetime.year + '/' + current_datetime.day + '/' + current_datetime.month +'\''
    hdu.header['TIME-OBS'] = '\'' + current_datetime.time() +'\''
    hdu.header['OBSERVER'] = '\'' + 'Observer' +'\''
    hdu.header['OBJECT'] = '\'' + 'Object' +'\''
    hdu.header['PROG-ID'] = '\'' + 'Programm ID' +'\''
    hdu.header['AUTHOR'] = '\'' + 'Author' +'\''
    hdu.header['DATAMAX'] = np.max(image_data)
    hdu.header['DATAMIN'] = np.min(image_data)
    hdu.header['FILE'] = '\'' + name +'\''
    hdu.header['IMAGETYP'] = '\'' + file_type +'\''
    hdu.header['START'] = hdu.header['TIME-OBS']
    hdu.header['EXPTIME'] = exp_time
    hdu.header['UT'] = '\'' + datetime.utcnow() + '\''
    hdu.header['ST'] = '\'' + sid_time + '\''
    hdu.header['RA'] = '\'' + star.ra + '\''
    hdu.header['DEC'] = '\'' + star.dec + '\''
    hdu.header['EPOCH'] = current_datetime.year + datetime.date.today().strftime("%j")/365
    hdu.header['Z'] = 90. - star.alt
    hdu.header['A'] = star.az
    hdu.header['SEEING'] = '\'' + seeing + '\''
    hdu.header['SLITWID'] = slit
    hdu.header['MIRRTEMP'] = mirrtemp
    hdu.header['DOMETEMP'] = dometemp
    hdu.header['OUTTEMP'] = outtemp
    hdu.header['WIND'] = wind
    hdu.header['CLOUDS'] = clouds
    hdu.header['PRESSURE'] = pressure
    hdu.header['MODE'] = '\'' + mode + '\''
    hdu.writeto(name)

class FitsWorker(QObject):
    fitsWritten = Signal()

    def __init__(self, lock: Lock):
        self.__lock = lock
        self.__stop_thread = False
        self.__path = ""

    def running(self):
        while self.__stop_thread == False:
            self.__lock.acquire(blocking=True)
            time.sleep(3)
            if self.__stop_thread == True:
                break
            path = self.__path
            window = Plot_image(path)
            window.show()

    @Slot(str)
    def set_fits_path(self, path: str):
        log.info("Got path to the fits file '{0}'".format(path))
        self.__path = path
        self.__lock.release()

    def stop_thread(self):
        self.__stop_thread = True
        self.__lock.release()

