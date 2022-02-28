from math import sin, cos, asin, acos, radians, degrees, atan2, pi

from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import time
from siderealtimeS0 import calculate_S0
from numpy import sign

import logger as log

#перевод "градусы-минуты-секунды" в "градусы"
def dms_to_d(d,m,s):    
    if d < 0:        
        d = d - m/60 - s/3600
    else:
        d = d + m/60 + s/3600    
    return d
    
#перевод "градусы" в "градусы-минуты-секунды"    
def d_to_dms(A):
    A=float(A)
    if A>=0:
        return (int(A), int(A*60%60), round(A*60%60*60%60,2))
    else:
        A*=-1
        return (-int(A), int(A*60%60), round(A*60%60*60%60,2))

#считает звездное время s, [S0] = h, [T] = h     
def calculate_s(S0, T): 
    longitude = dms_to_d(59, 32, 50.18)
    K = 366.2422/365.2422
    
    s = S0 - longitude*dms_to_d(0, 3, 56.56)/360 + T*K #h
    if s >= 24:
        s-=24
            
    return s # 0 <= s < 24



class Telescope:
    latitude = dms_to_d(57, 2, 12.1) #deg
    longitude = dms_to_d(59, 32, 50.18) #deg
    v_max = 6 # deg/s - максимальная скорость вращения телескопа по осям
    
    def __init__(self, alt = 15, az = 180, mode = 'A'):
        self.__alt = alt
        self.__az = az
        self.__mode = mode
    
    @property    
    def alt(self):
        return self.__alt
    
    @alt.setter
    def alt(self, h):
        if 15 <= h <= 85:
            self.__alt = h
        else:
            raise ValueError  #####error
    
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
            raise ValueError #print ("ModeError") #####error
        elif 300 < A < 360 and self.__mode == 'A':
            raise ValueError #print ("ModeError") #####error
        else:
            raise ValueError  #####error
            
    @property        
    def mode(self):
        return self.__mode
    
    @mode.setter
    def mode(self, string): ####нельзя использовать для смены режима!! см. change_mode(self)
        if string == 'A':
            self.__mode = 'A'
        elif string == 'B':
            self.__mode = 'B'
        else:
            raise ValueError   #####error
            
    
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
                
            
    

class Star:
    latitude = dms_to_d(57, 2, 12.1) #deg
    longitude = dms_to_d(59, 32, 50.18) #deg
        
    def __init__(self, ra = 0, dec = 0):        
        self.ra = ra #deg        
        self.dec = dec #deg
                      
                
    def eq_to_hor(self, s):        
        phi = radians(self.latitude)
        delta = radians(self.dec)
        alpha = radians(self.ra)
        
        t = radians(s*15) - alpha
        if t<0:
            t+=2*pi
            
        h = asin(sin(phi)*sin(delta)+cos(phi)*cos(delta)*cos(t))
        
        A = atan2(cos(delta)*sin(t), -cos(phi)*sin(delta)+sin(phi)*cos(delta)*cos(t))
        if A<0:
            A+=2*pi
        
        self.alt = degrees(h)
        self.az = degrees(A)
        
        return (self.alt, self.az)
    
    
