#!/usr/bin/python3

import threading as thr
import argparse
import sys
import time
sys.path.append("../src/")
# Write your imports from `src/` folder below
import te_coords as tcd
import logger as log
import te_fits as tft


#----------------------------------new------------------------------------------#

from astropy.io import fits
import numpy as np
from datetime import datetime
from math import sin, cos, floor, pi

# считывание fits-файла, возвращает отдельно данные (которые потом нужно переделать под экспозицию) и header
def read_fits(mode, file_type, exp_time):
    name = "./data/" + file_type + "_" + mode + '.fts'
    hdu = fits.open(name)
    image_data = hdu[0].data
    hdr = hdu[0].header
    #time.sleep(exp_time*0.01)   не ждет!!!
    return image_data, hdr

def change_fits_with_exposition(image_data, exp_time): #меняем fits под экспозицию
    tau = exp_time 
    image_data = image_data/900
    image_data = image_data*tau
    image_data[np.where(image_data>20000)] = 200000

    return image_data

def write_fits(countfile, image_data, hdr, path, file_type, exp_time, star, sid_time, slit, weather, mode, focus):
    current_datetime = datetime.now()
    name = 's' + countfile + '.fts'
    mirrtemp, dometemp, outtemp, wind, clouds, pressure, seeing = get_weather(weather, focus)
    hdu = fits.PrimaryHDU(data = image_data)
    hdu.header = hdr
    star.eq_to_hor(sid_time)
    hdu.header['DATE'] = '\'' + str(current_datetime.date()) + '\''
    hdu.header['DATE-OBS'] = '\'' + str(current_datetime.year) + '/' + str(current_datetime.day) + '/' + str(current_datetime.month) +'\''
    hdu.header['TIME-OBS'] = '\'' + str(current_datetime.time()) +'\''
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
    hdu.header['UT'] = '\'' + str(datetime.utcnow()) + '\''
    hdu.header['ST'] = '\'' + str(sid_time) + '\''
    hdu.header['RA'] = '\'' + str(star._ra) + '\''
    hdu.header['DEC'] = '\'' + str(star._dec) + '\''
    hdu.header['EPOCH'] = str(current_datetime)
    hdu.header['Z'] = 90. - star.alt
    hdu.header['A'] = star.az
    hdu.header['SEEING'] = '\'' + str(seeing) + '\''
    hdu.header['SLITWID'] = slit
    hdu.header['MIRRTEMP'] = mirrtemp
    hdu.header['DOMETEMP'] = dometemp
    hdu.header['OUTTEMP'] = outtemp
    hdu.header['WIND'] = wind
    hdu.header['CLOUDS'] = clouds
    hdu.header['PRESSURE'] = pressure
    hdu.header['MODE'] = '\'' + mode + '\''
    hdu.writeto(name)

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

def dms_to_d(d: int, m: int, s: float) -> float:    
    if d < 0:        
        d = d - m / 60 - s / 3600
    else:
        d = d + m / 60 + s / 3600    
    return d

#----------------------------------new------------------------------------------#







def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple telescope emulator")
    parser.add_argument("--debug", action="store_true", help="Stores additional debug info into log file")
    parser.add_argument("--log-path", default="log.txt", help="Path to the log file. Default: 'log.txt'")

    args = vars(parser.parse_args())
    is_debug = args.pop("debug")
    log_path = args["log_path"]

    # Setup logger
    log_level = 'INFO'
    if is_debug == True:
        log_level = 'DEBUG'

    log.setup_logger(log_level, log_path)

    lock = thr.Lock()
    tel = tcd.Telescope()
    star = tcd.Star(20, 30)
    log.info("Initializing")
    proc = thr.Thread(target=tel.running, args=(lock,))
    proc.start()
    time.sleep(3)
    for i in range(9):
        log.debug("Iteration number {0}".format(i))
        tel.proceed_movement(lock, 40, 50)
        #time.sleep(1)

    tel.stop_thread(lock)

    proc.join()
    
    
#----------------------------------new------------------------------------------#   
    
    #чтение фитса
    exp_time = 900      #из интерфейса
    mode = "spectra"  #из интерфейса
    file_type ="obj"  #из интерфейса
    image_data, hdr = read_fits(mode, file_type, exp_time)
    
    #изменяем кадр под заданную экспозицию
    image_data = change_fits_with_exposition(image_data, exp_time)

    #записываем новый фитс
    #нужно текущее звездное время:
    date = time.localtime(time.time())
    s_0 = calculate_s0(date)
    s_0 = dms_to_d(s_0[0], s_0[1], s_0[2])
    t = dms_to_d(date.tm_hour, date.tm_min, date.tm_sec)
    sid_time = calculate_s(s_0, t)
    
    #другие параметры из интерфейса(?)
    countfile = "1" #название файла
    slit = 1 #ширина щели
    weather = 'good'
    focus = True
    
    write_fits(countfile, image_data, hdr, None, file_type, exp_time, star, sid_time, slit, weather, mode, focus)
   



    
#----------------------------------new------------------------------------------#  
    
    
    
    
    
    
    
    
    
    
    

if __name__ == '__main__':
    sys.exit(main())
