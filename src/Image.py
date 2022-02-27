from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
import PyQt5.QtWidgets as Qt
import matplotlib.patches as patches
import sys
import numpy as np
from astropy.io import fits
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import LogNorm

class Plot_image(Qt.QMainWindow):
    def __init__(self, ):
        super().__init__()
        
        # Параметры (передаются извне, как - не знаю)
        self.name_fits='s19450501.fts' # Название файла
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
        self.label = Qt.QLabel()
        self.label.setFont(QFont('Arial', 10))

        # Отображение положения щели
        self.checkbox=Qt.QCheckBox('Slit')
        self.checkbox.setFont(QFont('Arial', 10))
        self.checkbox.stateChanged.connect(self.plot_slit)

        # Изменение цветовой схемы
        self.label2 = Qt.QLabel('Min value') 
        self.label2.setFont(QFont('Arial', 10))
        self.input1 = Qt.QLineEdit()
        self.input1.textChanged.connect(self.min_max_value)
        self.label3 = Qt.QLabel('Max value')
        self.label3.setFont(QFont('Arial', 10))
        self.input2 = Qt.QLineEdit()
        self.input2.textChanged.connect(self.min_max_value)
        self.checkbox2=Qt.QCheckBox('Log norm color')
        self.checkbox2.setFont(QFont('Arial', 10))
        self.checkbox2.stateChanged.connect(self.color_norm)
        
        # Дополнительное изображение (срез)
        self.figure2 = Figure(figsize=(7, 3))
        self.canvas2 = FigureCanvas(self.figure2)
        self.ax2 = self.figure2.subplots()
        self.canvas2.draw()
        
        # Вывод на экран
        layout = Qt.QVBoxLayout()
        splitter = Qt.QSplitter()
        splitter2 = Qt.QSplitter()
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
        widget = Qt.QWidget()
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
        binning=self.h['BINNING'] # бининг по оси x
        n=binning.index('x')
        n_p=float(binning[0:n]) # 
        width_slit=self.h['SLITWID'] # ширина щели в "
        scale=self.h['IMSCALE'] # масштаб по оси x в "/Pix
        n=scale.index('x')
        scale=float(scale[0:n]) #
        #
        self.width=width_slit/scale/n_p # Ширина щели в Pix

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
        
    

app=Qt.QApplication(sys.argv)
window=Plot_image()
window.show()
app.exec()

