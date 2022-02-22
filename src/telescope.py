from math import sin, cos, asin, acos, radians, degrees, atan2, pi
#import requests
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
#from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import time
from S0 import calculate_S0

#import astroplan
#astroplan.test()
#from astroplan import download_IERS_A
#download_IERS_A()

#перевод градусы-минуты-секунды в градусы
def dms_to_d(d,m,s):    
    if d < 0:        
        d = d - m/60 - s/3600
    else:
        d = d + m/60 + s/3600    
    return d
    
#перевод градусы в градусы-минуты-секунды    
def d_to_dms(A):
    A=float(A)
    if A>=0:
        return (int(A), int(A*60%60), round(A*60%60*60%60,2))
    else:
        A*=-1
        return (-int(A), int(A*60%60), round(A*60%60*60%60,2))

#считает звездное время s     
def calculate_s():
    longitude = 59.55
    K = 366.2422/365.2422
        
    S0 = (9, 59, 38.1775) #hms
    S0 = dms_to_d(S0[0], S0[1], S0[2]) #h
        
    T = (22, 0, 0) #hms
    T = dms_to_d(T[0], T[1], T[2]) #h
        
    s = S0 - longitude*dms_to_d(0, 3, 56.56)/360 + T*K #h
    if s >= 24:
        s-=24
            
    return s # 0 <= s < 24



class Telescope:
    latitude = 57.03 #deg
    longitude = 59.55 #deg
    v_max = 6 # deg/s - максимальная скорость вращения телескопа по осям
    
    def __init__(self, alt = 10, az = 0):
        self.__alt = alt
        self.__az = az
    
    @property    
    def alt(self):
        return self.__alt
    
    @alt.setter
    def alt(self, h):
        if 10 <= h <= 80:
            self.__alt = h
        else:
            raise ValueError
    
    @property        
    def az(self):
        return self.__az
    
    @az.setter
    def az(self, A):
        if 0 <= A < 360:
            self.__az = A
        else:
            raise ValueError
            
    
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
        

    def move_to_star(self, star, t0):
        s = calculate_s()  ##добавить t0 - время начала движения
        h_star, A_star = star.eq_to_hor(s)
        
        while abs(star.alt-self.alt)>0.1/3600 or abs(star.az-self.az)>0.1/3600:
            h_star_in1sec, A_star_in1sec = star.eq_to_hor(s+1/3600)
            
            d_h = abs(self.alt - h_star_in1sec)
            d_A = abs(self.az - A_star_in1sec)
            
            if d_h <= self.v_max and d_A <= self.v_max:
                self.alt = h_star_in1sec
                self.az = A_star_in1sec
    
            if d_h <= self.v_max and d_A > self.v_max:
                self.alt = h_star_in1sec
                self.az += self.v_max
                
            if d_h > self.v_max and d_A <= self.v_max:
                self.alt += self.v_max
                self.az = A_star_in1sec            
            
            if d_h > self.v_max and d_A > self.v_max:
                self.alt += self.v_max
                self.az += self.v_max
                
            s+=1/3600
            time.sleep(1)
            #print(star.alt, star.az)   ###тут тестить
            #print(self.alt, self.az)
            
        
    

class Star:
    latitude = 57.03 #deg
    longitude = 59.55 #deg
        
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

        



        
#t = Time(datetime(2002, 2, 21, 0, 0, 0), scale='utc')
#print(t.sidereal_time('mean', 'greenwich'))    
        
#observing_location = EarthLocation(lat=57.03*u.deg, lon=59.55*u.deg)
#observing_time = Time('2012-7-12 23:00:00', scale='utc', location=observing_location)
#LST = observing_time.sidereal_time('mean')
#print(LST)

'''     тут тестить
t = Telescope()
star = Star(70, 40)
s = calculate_s()

print(star.eq_to_hor(s))
print(t.alt, t.az)

t.move_to_star(star, 22)
'''



