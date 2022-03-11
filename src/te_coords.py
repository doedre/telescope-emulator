from PySide6.QtCore import QObject, Signal, Slot
from threading import Thread, Lock

from math import *
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import time
from numpy import sign

import logger as log

# перевод "градусы-минуты-секунды" в "градусы"
def dms_to_d(d: int, m: int, s: float) -> float:    
    if d < 0:        
        d = d - m / 60 - s / 3600
    else:
        d = d + m / 60 + s / 3600    
    return d
    
# перевод "градусы" в "градусы-минуты-секунды"    
def d_to_dms(A: float):
    A = float(A)
    if A >= 0:
        return (int(A), int(A*60%60), round(A*60%60*60%60,2))
    else:
        A *= -1
        return (-int(A), int(A*60%60), round(A*60%60*60%60,2))

# считает звездное время s, [S0] = h, [T] = h     
def calculate_s(S0: float, T: float) -> float: 
    longitude = dms_to_d(59, 32, 50.18)
    K = 366.2422 / 365.2422
    
    s = S0 - longitude * dms_to_d(0, 3, 56.56) / 360 + T * K #h
    if s >= 24:
        s -= 24
            
    return s # 0 <= s < 24


def calculate_S0(date):  #можно заменить date на (число, месяц, год)
    im = date.tm_mon
    iday = date.tm_mday
    iyear = date.tm_year
    r = 1296000.0
    
    month = [31,28,31,30,31,30,31,31,30,31,30,31]
    
    if im != 1:
        tmp = floor(iyear/4)
        i = 4 * tmp
        if iyear == i:
            month[1] = 29
        for j in month[:im-1]:
            iday += j
    
    iy = iyear - 1900
    iday = floor((iday-1)+(iy-1)/4)
    
    t=iday + iy*365.0
    t = (t+0.5)/36525.0
    t = t - 1
    
    sm = 24110.548410 + 8640184.8128660*t + 0.093104*t*t- 0.00000620*t*t*t
    while sm <= 0:
        sm = sm + 86400.0
    while sm > 86400:
        sm = sm - 86400.0
    
    p = pi/180.0/3600.0 
    
    e = p*(84381.448 - 46.8150*t - 0.00059*t*t + 0.0018130*t*t*t) 
    
    q = p*( 450160.280 -   5.0*r*t - 482890.539*t+ 7.455*t*t + 0.0080*t*t*t) 
    d = p*(1072261.3070 + 1236.0*r*t + 1105601.328*t - 6.891*t*t+ 0.0190*t*t*t) 
    f = p*( 335778.8770 + 1342.0*r*t + 295263.1370*t - 13.2570*t*t+ 0.0110*t*t*t) 
    m = p*(1287099.804 +  99.0*r*t+1292581.2240*t -  0.5770*t*t - 0.0120*t*t*t) 
    l = p*( 485866.7330+1325.0*r*t + 715922.633*t + 31.3100*t*t+ 0.0640*t*t*t) 
    
    pl =  -(17.19960 + 0.017420*t)*sin(q) 
    
    pl = pl + (0.20620 + 0.000020*t)*sin(2.0*q) 
    pl = pl +   0.00460            *sin(q+2.0*f-2.0*l) 
    pl = pl +   0.00110            *sin(2.0*(l-f)) 
    pl = pl -   0.00030            *sin(2.0*(q+f-l)) 
    pl = pl-   0.00030            * sin (l-m-d) 
    pl = pl-   0.00020            * sin (q-2.0*d+2.0*f-2.0*m) 
    pl = pl+   0.00010            * sin (q-2.0*f+2.0*l) 
    pl = pl-( 1.31870+ 0.000160*t)* sin (2.0*(q-d+f)) 
    pl = pl+(  0.14260-0.000340*t)* sin (m) 
    pl = pl-(  0.05170-0.000120*t)* sin (2.0*q-2.0*d+2.0*f+m) 
    pl = pl+(  0.02170-0.000050*t)* sin (2.0*q-2.0*d+2.0*f-m) 
    pl = pl+(  0.01290+0.000010*t)* sin (q-2.0*d+2.0*f) 
    pl = pl+   0.00480            * sin (2.0*(l-d)) 
    pl = pl-   0.00220            * sin (2.0*(f-d)) 
    pl = pl+(  0.00170-0.000010*t)* sin (2.0*m) 
    pl = pl-   0.00150            * sin (q+m) 
    pl = pl-(  0.00160-0.000010*t)* sin (2.0*(q-d+f+m)) 
    pl = pl-   0.00120            * sin (q-m) 
    pl = pl-   0.00060            * sin (q+2.0*d-2.0*l) 
    pl = pl-   0.00050            * sin (q-2.0*d+2.0*f-m) 
    pl = pl+   0.00040            * sin (q-2.0*d+2.0*l) 
    pl = pl+   0.00040            * sin (q-2.0*d+2.0*f+m) 
    pl = pl-   0.00040            * sin (l-d) 
    pl = pl+   0.00010            * sin (2.0*l+m-2.0*d) 
    pl = pl+   0.00010            * sin (q+2.0*d-2.0*f) 
    pl = pl-   0.00010            * sin (2.0*d-2.0*f+m) 
    pl = pl+   0.00010            * sin (2.0*q+m) 
    pl = pl+   0.00010            * sin (q+d-l) 
    pl = pl-   0.00010            * sin (m+2.0*f-2.0*d) 
    
    ps =   -(  0.22740+0.000020*t)* sin (2.0*(q+f)) 
    ps = ps+(  0.07120+0.000010*t)* sin (l) 
    ps = ps-(  0.03860+0.000040*t)* sin (q+2.0*f) 
    ps = ps-   0.03010            * sin (2.0*q+2.0*f+l) 
    ps = ps-   0.01580            * sin (l-2.0*d) 
    ps = ps+   0.01230            * sin (2.0*q+2.0*f-l) 
    ps = ps+   0.00630            * sin (2.0*d) 
    ps = ps+(  0.00630+0.000010*t)* sin (q+l) 
    ps = ps-(  0.00580+0.000010*t)* sin (q-l) 
    ps = ps-   0.00590            * sin (2.0*q+2.0*d+2.0*f-l) 
    ps = ps-   0.00510            * sin (q+2.0*f+l) 
    ps = ps-   0.00380            * sin (2.0*(q+d+f)) 
    ps = ps+   0.00290            * sin (2.0*l) 
    ps = ps+   0.00290            * sin (2.0*q-2.0*d+2.0*f+l) 
    ps = ps-   0.00310            * sin (2.0*(q+f+l)) 
    ps = ps+   0.00260            * sin (2.0*f) 
    ps = ps+   0.00210            * sin (q+2.0*f-l) 
    ps = ps+   0.00160            * sin (q+2.0*d-l) 
    ps = ps-   0.00130            * sin (q-2.0*d+l) 
    ps = ps-   0.00100            * sin (q+2.0*d+2.0*f-l) 
    ps = ps-   0.00070            * sin (l+m-2.0*d) 
    ps = ps+   0.00070            * sin (2.0*q+2.0*f+m) 
    ps = ps-   0.00070            * sin (2.0*q+2.0*f-m) 
    ps = ps-   0.00080            * sin (2.0*q+2.0*d+2.0*f+l) 
    ps = ps+   0.00060            * sin (2.0*d+l) 
    ps = ps+   0.00060            * sin (2.0*(q-d+f+l)) 
    ps = ps-   0.00060            * sin (q+2.0*d) 
    ps = ps-   0.00070            * sin (q+2.0*d+2.0*f) 
    ps = ps+   0.00060            * sin (q-2.0*d+2.0*f+l) 
    ps = ps-   0.00050            * sin (q-2.0*d) 
    ps = ps+   0.00050            * sin (l-m) 
    ps = ps-   0.00050            * sin (q+2.0*f+2.0*l) 
    ps = ps-   0.00040            * sin (m-2.0*d) 
    ps = ps+   0.00040            * sin (l-2.0*f) 
    ps = ps-   0.00040            * sin (d) 
    ps = ps-   0.00030            * sin (l+m) 
    ps = ps+   0.00030            * sin (l+2.0*f) 
    ps = ps-   0.00030            * sin (2.0*q+2.0*f-m+l) 
    ps = ps-   0.00030            * sin (2.0*q+2.0*d+2.0*f-m-l) 
    ps = ps-   0.00020            * sin (q-2.0*l) 
    ps = ps-   0.00030            * sin (2.0*q+2.0*f+3.0*l) 
    ps = ps-   0.00030            * sin (2.0*q+2.0*d+2.0*f-m) 
    ps = ps+   0.00020            * sin (2.0*q+2.0*f+m+l) 
    ps = ps-   0.00020            * sin (q-2.0*d+2.0*f-l) 
    ps = ps+   0.00020            * sin (q+2.0*l) 
    ps = ps-   0.00020            * sin (2.0*q+l) 
    ps = ps+   0.00020            * sin (3.0*l) 
    ps = ps+   0.00020            * sin (2.0*q+d+2.0*f) 
    ps = ps+   0.00010            * sin (2.0*q-l) 
    ps = ps-   0.00010            * sin (l-4.0*d) 
    ps = ps+   0.00010            * sin (2.0*(q+d+f-l)) 
    ps = ps-   0.00020            * sin (2.0*q+4.0*d+2.0*f-l) 
    ps = ps-   0.00010            * sin (2.0*l-4.0*d) 
    ps = ps+   0.00010            * sin (2.0*q-2.0*d+2.0*f+m+l) 
    ps = ps-   0.00010            * sin (q+2.0*d+2.0*f+l) 
    ps = ps-   0.00010            * sin (2.0*q+4.0*d+2.0*f-2.0*l) 
    ps = ps+   0.00010            * sin (2.0*q+4.0*f-l) 
    ps = ps+   0.00010            * sin (l-m-2.0*d) 
    ps = ps+   0.00010            * sin (q-2.0*d+2.0*f+2.0*l) 
    ps = ps-   0.00010            * sin (2.0*(q+d+f+l)) 
    ps = ps-   0.00010            * sin (q+2.0*d+l) 
    ps = ps+   0.00010            * sin (2.0*q-2.0*d+4.0*f) 
    ps = ps+   0.00010            * sin (2.0*q-2.0*d+2.0*f+3.0*l) 
    ps = ps-   0.00010            * sin (l+2.0*f-2.0*d) 
    ps = ps+   0.00010            * sin (q+2.0*f+m) 
    ps = ps+   0.00010            * sin (q+2.0*d-m-l) 
    ps = ps-   0.00010            * sin (q-2.0*f) 
    ps = ps-   0.00010            * sin (2.0*q-d+2.0*f) 
    ps = ps-   0.00010            * sin (2.0*d+m) 
    ps = ps-   0.00010            * sin (l-2.0*f-2.0*d) 
    ps = ps-   0.00010            * sin (q+2.0*f-m) 
    ps = ps-   0.00010            * sin (q-2.0*d+m+l) 
    ps = ps-   0.00010            * sin (l-2.0*f+2.0*d) 
    ps = ps+   0.00010            * sin (2.0*(l+d)) 
    ps = ps-   0.00010            * sin (2.0*q+4.0*d+2.0*f) 
    ps = ps+   0.00010            * sin (d+m) 
    
    s0 = sm+(pl+ps)/15.0* cos(e) 

    s_hour = floor(s0/3600) 
    s_min = floor((s0-s_hour*3600)/60) 
    s_sec = floor((s0-s_hour*3600-s_min*60)*10000)/10000
    
    return (s_hour, s_min, s_sec)

class Star:
    latitude = dms_to_d(57, 2, 12.1) #deg
    longitude = dms_to_d(59, 32, 50.18) #deg
        
    def __init__(self, ra = 0, dec = 0):        
        self._ra = ra #deg        
        self._dec = dec #deg
                
    def eq_to_hor(self, s):        
        phi = radians(self.latitude)
        delta = radians(self._dec)
        alpha = radians(self._ra)
        
        t = radians(s * 15) - alpha
        if t < 0:
            t += 2 * pi
            
        h = asin(sin(phi)*sin(delta)+cos(phi)*cos(delta)*cos(t))
        
        A = atan2(cos(delta)*sin(t), -cos(phi)*sin(delta)+sin(phi)*cos(delta)*cos(t))
        if A < 0:
            A += 2 * pi
        
        self.alt = degrees(h)
        self.az = degrees(A)
        
        return (self.alt, self.az)
 
class Telescope(QObject):
    _latitude = dms_to_d(57, 2, 12.1) #deg
    _longitude = dms_to_d(59, 32, 50.18) #deg
    _v_max = 6 # deg/s - максимальная скорость вращения телескопа по осям

    def __init__(self, parent=None):
        super().__init__()
        self.__alt = 25
        self.__az = 180
        self.__ra = 0
        self.__dec = 0
        self.__mode = 'A'
        self.__stop_thread = False
        self.__is_parked = True

    telescopeMoved = Signal(float, float)
    coordinatesError = Signal(str)

    @property    
    def alt(self):
        return self.__alt
    
    @alt.setter
    def alt(self, h):
        if 15 <= h <= 85:
            self.__alt = h
        else:
            self.coordinatesError.emit("'h' = {0} is out of range".format(h))
            log.warn("'h' = {0} is out of range".format(h))
    
    @property        
    def az(self):
        return self.__az
    
    @az.setter
    def az(self, A):
        if 0 <= A <= 300 and self.__mode == 'A':
            self.__az = A
        elif (70 <= A < 360 or 0 <= A <=10) and self.__mode == 'B':
            self.__az = A
        elif 10 < A < 70 and self.__mode == 'B':
            self.coordinatesError.emit("'A' = {0} is out of range".format(A))
            log.warn("'A' = {0} is out of range".format(A))
        elif 300 < A < 360 and self.__mode == 'A':
            self.coordinatesError.emit("'A' = {0} is out of range".format(A))
            log.warn("'A' = {0} is out of range".format(A))
        else:
            self.coordinatesError.emit("'A' = {0} is out of range".format(A))
            log.warn("'A' = {0} is out of range".format(A))
            
    @property        
    def mode(self):
        return self.__mode
    
    @mode.setter
    def mode(self, string): ####нельзя использовать для смены режима!! см. change_mode(self)
        if string == 'A':
            self.__mode = 'A'
        elif string == 'B':
            self.__mode = 'B'

    @property
    def ra(self) -> float:
        return self.__ra

    @ra.setter
    def ra(self, right_ascension: float):
        self.__ra = right_ascension

    @property
    def dec(self) -> float:
        return self.__dec

    @dec.setter
    def dec(self, declination: float):
        self.__dec = declination

    def stop_thread(self, lock: Lock):
        self.__stop_thread = True
        if lock.locked():
            lock.release()

    def date(self):
        return time.localtime(time.time())

    def proceed_movement(self, lock: Lock, ra: float, dec: float):
        self.__ra = ra
        self.__dec = dec
        if lock.locked():
            lock.release()

    def running(self, lock: Lock):
        while self.__stop_thread == False:
            log.debug("Lock movement thread")
            lock.acquire(blocking=True)
            log.debug("Unlock movement thread")
            if self.__stop_thread == True:
                break

            if self.__is_parked == True:
                log.debug("Parking telescope")
                d_A = 180 - self.az
                d_h = 15 - self.alt
                if abs(d_A) > self._v_max:
                    self.az += np.sign(d_A) * self._v_max
                    d_A = 180 - self.az
                if abs(d_h) > self._v_max:
                    self.alt += np.sign(d_h) * self._v_max
                    d_h = 15 - self.alt

                log.debug("Set new parameters | alt: {0} | az: {1}".format(self.alt, self.az))
                self.telescopeMoved.emit(self.alt, self.az)
                continue

            # Read parameters to local variables to exclude race conditions
            date = self.date()
            S_0 = calculate_S0(date)
            S_0 = dms_to_d(S_0[0], S_0[1], S_0[2])
            T = dms_to_d(date.tm_hour, date.tm_min, date.tm_sec)
            s = calculate_s(S_0, T)
            star = Star(self.__ra, self.__dec)
            star_h, star_A = star.eq_to_hor(s)

            delta_h = star_h - self.alt
            delta_A = star_A - self.az

            # Set new coordinates depending on current time
            if abs(delta_h) <= self._v_max and abs(delta_A) <= self._v_max:
                self.alt = star_h
                self.az = star_A
            elif abs(delta_h) <= self._v_max and abs(delta_A) > self._v_max:
                self.alt = star_h
                self.az = self.az + sign(delta_A) * self._v_max
            elif abs(delta_h) > self._v_max and abs(delta_A) <= self._v_max:
                self.alt = self.alt + sign(delta_h) * self._v_max
                self.az = star_A
            elif abs(delta_h) > self._v_max and abs(delta_A) > self._v_max:
                self.alt = self.alt + sign(delta_h) * self._v_max
                self.az = self.az + sign(delta_A) * self._v_max

            log.debug("Set new parameters | alt: {0} | az: {1}".format(self.alt, self.az))
            self.telescopeMoved.emit(self.alt, self.az)

    def worker(self, lock: Lock):
        while self.__stop_thread == False:
            self.proceed_movement(lock, self.__ra, self.__dec)
            time.sleep(1)
    @Slot()
    def park_telescope(self):
        log.info("Start to park telescope")
        self.__is_parked = True
    
    @Slot(float, float)
    def set_star_coords(self, ra: float, dec: float):
        log.info("Moving to {0} {1}".format(ra, dec))
        self.__is_parked = False
        self.__ra = ra
        self.__dec = dec

    #считает прямое восхождение и склонение точки (h, A) в момент звездного времени s
    def hor_to_eq(self, s):
        phi = radians(self.latitude)
        h = radians(self.alt)
        A = radians(self.az)

        delta = asin(sin(phi)*sin(h) - cos(phi)*cos(h)*cos(A)) # -pi/2 <= delta <= pi/2
        
        t = atan2(cos(h)*sin(A), cos(phi)*sin(h)+sin(phi)*cos(h)*cos(A)) # -pi < t < pi
        if t<0:
            t+=2*pi # 0 <= t < 2 pi

        alpha = radians(s*15) - t # rad
        if alpha<0:
            alpha+=2*pi

        self.ra = degrees(alpha)  # 0 <= RA < 360 deg
        self.dec = degrees(delta) # -90 <= DEC <= 90 deg
        
        return (self.ra, self.dec)
        
    
    #наведение на звезду, date - объект типа time.struct_time, время начала наведения (момент вызова функции)
    def move_to_star(self, star, date):
        S0 = calculate_S0(date)
        S0 = dms_to_d(S0[0], S0[1], S0[2])
        T = dms_to_d(date.tm_hour, date.tm_min, date.tm_sec)
        s = calculate_s(S0, T)
        h_star, A_star = star.eq_to_hor(s)
        
        while abs(star.alt-self.alt)>0.1/3600 or abs(star.az-self.az)>0.1/3600:
            h_star_in1sec, A_star_in1sec = star.eq_to_hor(s+1/3600)
            
            d_h = h_star_in1sec - self.alt
            d_A = A_star_in1sec - self.az
            
            if abs(d_h) <= self.v_max and abs(d_A) <= self.v_max:
                self.alt = h_star_in1sec
                self.az = A_star_in1sec
    
            if abs(d_h) <= self.v_max and abs(d_A) > self.v_max:
                self.alt = h_star_in1sec
                self.az = self.az + sign(d_A)*self.v_max
                
            if abs(d_h) > self.v_max and abs(d_A) <= self.v_max:
                self.alt = self.alt + sign(d_h)*self.v_max
                self.az = A_star_in1sec            
            
            if abs(d_h) > self.v_max and abs(d_A) > self.v_max:
                self.alt = self.alt + sign(d_h)*self.v_max
                self.az = self.az + sign(d_A)*self.v_max
                
            s+=1/3600
            time.sleep(1)
            #print(star.alt, star.az)   ###info
            #print(self.alt, self.az)
            
    
    #ведение телескопа с момента времени date в течение tau. date - объект time.struct_time, tau в секундах(?)
    def guidance(self, star, date, tau):
        S0 = calculate_S0(date)
        S0 = dms_to_d(S0[0], S0[1], S0[2])
        T = dms_to_d(date.tm_hour, date.tm_min, date.tm_sec)
        s = calculate_s(S0, T)
        
        for i in range(tau):
            h_star, A_star = star.eq_to_hor(s)
            self.alt = h_star
            self.az = A_star
            s+=1/3600
            time.sleep(1)
            
            #print(star.alt, star.az)   ###info
            #print(self.alt, self.az)
            
    #меняет режим телескопа
    def change_mode(self):
        if self.mode == 'A':
            if 70 <= self.az <= 300:
                self.mode = 'B'
            elif 0 <= self.az < 70:                
                while self.az < 70-self.v_max:
                    self.az += self.v_max
                    time.sleep(1)
                    #print (self.az) ###info
                self.az = 70
                time.sleep(1)
                #print (self.az) ###info
                self.mode = 'B'
            else:
                raise ValueError #print ('ChangeModeError') ###error
                
        elif self.mode == 'B':
            if 70 <= self.az <= 300:
                self.mode = 'A'
            elif 300 < self.az < 360 or 0 <= self.az <= 10:
                if self.az <= 10:
                    while self.az >= self.v_max:
                        self.az -= self.v_max
                        time.sleep(1)
                        #print (self.az) ###debug
                    self.az = self.az + 360 - self.v_max
                    time.sleep(1)  
                    #print (self.az) ###debug
                while self.az > 300+self.v_max:
                    self.az -= self.v_max
                    time.sleep(1)
                    #print (self.az) ###debug
                self.az = 300
                time.sleep(1)
                #print (self.az) ###debug
                self.mode = 'A'
            else:
                raise ValueError #print ('ChangeModeError')  ###error
                
    
    def parking(self):
        d_A = 180 - self.az
        d_h = 15 - self.alt
        while abs(d_A) > self.v_max or abs(d_h) > self.v_max:
            if abs(d_A) > self.v_max:
                self.az += np.sign(d_A) * self.v_max
                d_A = 180 - self.az
            if abs(d_h) > self.v_max:
                self.alt += np.sign(d_h) * self.v_max
                d_h = 15 - self.alt
            #print(self.az, self.alt) ###debug
            time.sleep(1)
        self.az = 180
        self.alt = 15
        #print(self.az, self.alt) ###debug
        time.sleep(1)
