import time
import math

#date = time.gmtime(time.time())

def calculate_S0(date):  #можно заменить date на (число, месяц, год)
    im = date.tm_mon
    iday = date.tm_mday
    iyear = date.tm_year
    r = 1296000.0
    
    month = [31,28,31,30,31,30,31,31,30,31,30,31]
    
    if im != 1:
        tmp = math.floor(iyear/4)
        i=4*tmp
        if iyear == i:
            month[1] = 29
        for j in month[:im-1]:
            iday += j
    
    iy = iyear - 1900
    iday = math.floor((iday-1)+(iy-1)/4)
    
    t=iday + iy*365.0
    t = (t+0.5)/36525.0
    t = t - 1
    
    sm = 24110.548410 + 8640184.8128660*t + 0.093104*t*t- 0.00000620*t*t*t
    while sm <= 0:
        sm = sm + 86400.0
    while sm > 86400:
        sm = sm - 86400.0
    
    p = math.pi/180.0/3600.0 
    
    e = p*(84381.448 - 46.8150*t - 0.00059*t*t + 0.0018130*t*t*t) 
    
    q = p*( 450160.280 -   5.0*r*t - 482890.539*t+ 7.455*t*t + 0.0080*t*t*t) 
    d = p*(1072261.3070 + 1236.0*r*t + 1105601.328*t - 6.891*t*t+ 0.0190*t*t*t) 
    f = p*( 335778.8770 + 1342.0*r*t + 295263.1370*t - 13.2570*t*t+ 0.0110*t*t*t) 
    m = p*(1287099.804 +  99.0*r*t+1292581.2240*t -  0.5770*t*t - 0.0120*t*t*t) 
    l = p*( 485866.7330+1325.0*r*t + 715922.633*t + 31.3100*t*t+ 0.0640*t*t*t) 
    
    pl =  -(17.19960 + 0.017420*t)*math.sin(q) 
    
    pl = pl + (0.20620 + 0.000020*t)*math.sin(2.0*q) 
    pl = pl +   0.00460            *math.sin(q+2.0*f-2.0*l) 
    pl = pl +   0.00110            *math.sin(2.0*(l-f)) 
    pl = pl -   0.00030            *math.sin(2.0*(q+f-l)) 
    pl = pl-   0.00030            * math.sin (l-m-d) 
    pl = pl-   0.00020            * math.sin (q-2.0*d+2.0*f-2.0*m) 
    pl = pl+   0.00010            * math.sin (q-2.0*f+2.0*l) 
    pl = pl-( 1.31870+ 0.000160*t)* math.sin (2.0*(q-d+f)) 
    pl = pl+(  0.14260-0.000340*t)* math.sin (m) 
    pl = pl-(  0.05170-0.000120*t)* math.sin (2.0*q-2.0*d+2.0*f+m) 
    pl = pl+(  0.02170-0.000050*t)* math.sin (2.0*q-2.0*d+2.0*f-m) 
    pl = pl+(  0.01290+0.000010*t)* math.sin (q-2.0*d+2.0*f) 
    pl = pl+   0.00480            * math.sin (2.0*(l-d)) 
    pl = pl-   0.00220            * math.sin (2.0*(f-d)) 
    pl = pl+(  0.00170-0.000010*t)* math.sin (2.0*m) 
    pl = pl-   0.00150            * math.sin (q+m) 
    pl = pl-(  0.00160-0.000010*t)* math.sin (2.0*(q-d+f+m)) 
    pl = pl-   0.00120            * math.sin (q-m) 
    pl = pl-   0.00060            * math.sin (q+2.0*d-2.0*l) 
    pl = pl-   0.00050            * math.sin (q-2.0*d+2.0*f-m) 
    pl = pl+   0.00040            * math.sin (q-2.0*d+2.0*l) 
    pl = pl+   0.00040            * math.sin (q-2.0*d+2.0*f+m) 
    pl = pl-   0.00040            * math.sin (l-d) 
    pl = pl+   0.00010            * math.sin (2.0*l+m-2.0*d) 
    pl = pl+   0.00010            * math.sin (q+2.0*d-2.0*f) 
    pl = pl-   0.00010            * math.sin (2.0*d-2.0*f+m) 
    pl = pl+   0.00010            * math.sin (2.0*q+m) 
    pl = pl+   0.00010            * math.sin (q+d-l) 
    pl = pl-   0.00010            * math.sin (m+2.0*f-2.0*d) 
    
    ps =   -(  0.22740+0.000020*t)* math.sin (2.0*(q+f)) 
    ps = ps+(  0.07120+0.000010*t)* math.sin (l) 
    ps = ps-(  0.03860+0.000040*t)* math.sin (q+2.0*f) 
    ps = ps-   0.03010            * math.sin (2.0*q+2.0*f+l) 
    ps = ps-   0.01580            * math.sin (l-2.0*d) 
    ps = ps+   0.01230            * math.sin (2.0*q+2.0*f-l) 
    ps = ps+   0.00630            * math.sin (2.0*d) 
    ps = ps+(  0.00630+0.000010*t)* math.sin (q+l) 
    ps = ps-(  0.00580+0.000010*t)* math.sin (q-l) 
    ps = ps-   0.00590            * math.sin (2.0*q+2.0*d+2.0*f-l) 
    ps = ps-   0.00510            * math.sin (q+2.0*f+l) 
    ps = ps-   0.00380            * math.sin (2.0*(q+d+f)) 
    ps = ps+   0.00290            * math.sin (2.0*l) 
    ps = ps+   0.00290            * math.sin (2.0*q-2.0*d+2.0*f+l) 
    ps = ps-   0.00310            * math.sin (2.0*(q+f+l)) 
    ps = ps+   0.00260            * math.sin (2.0*f) 
    ps = ps+   0.00210            * math.sin (q+2.0*f-l) 
    ps = ps+   0.00160            * math.sin (q+2.0*d-l) 
    ps = ps-   0.00130            * math.sin (q-2.0*d+l) 
    ps = ps-   0.00100            * math.sin (q+2.0*d+2.0*f-l) 
    ps = ps-   0.00070            * math.sin (l+m-2.0*d) 
    ps = ps+   0.00070            * math.sin (2.0*q+2.0*f+m) 
    ps = ps-   0.00070            * math.sin (2.0*q+2.0*f-m) 
    ps = ps-   0.00080            * math.sin (2.0*q+2.0*d+2.0*f+l) 
    ps = ps+   0.00060            * math.sin (2.0*d+l) 
    ps = ps+   0.00060            * math.sin (2.0*(q-d+f+l)) 
    ps = ps-   0.00060            * math.sin (q+2.0*d) 
    ps = ps-   0.00070            * math.sin (q+2.0*d+2.0*f) 
    ps = ps+   0.00060            * math.sin (q-2.0*d+2.0*f+l) 
    ps = ps-   0.00050            * math.sin (q-2.0*d) 
    ps = ps+   0.00050            * math.sin (l-m) 
    ps = ps-   0.00050            * math.sin (q+2.0*f+2.0*l) 
    ps = ps-   0.00040            * math.sin (m-2.0*d) 
    ps = ps+   0.00040            * math.sin (l-2.0*f) 
    ps = ps-   0.00040            * math.sin (d) 
    ps = ps-   0.00030            * math.sin (l+m) 
    ps = ps+   0.00030            * math.sin (l+2.0*f) 
    ps = ps-   0.00030            * math.sin (2.0*q+2.0*f-m+l) 
    ps = ps-   0.00030            * math.sin (2.0*q+2.0*d+2.0*f-m-l) 
    ps = ps-   0.00020            * math.sin (q-2.0*l) 
    ps = ps-   0.00030            * math.sin (2.0*q+2.0*f+3.0*l) 
    ps = ps-   0.00030            * math.sin (2.0*q+2.0*d+2.0*f-m) 
    ps = ps+   0.00020            * math.sin (2.0*q+2.0*f+m+l) 
    ps = ps-   0.00020            * math.sin (q-2.0*d+2.0*f-l) 
    ps = ps+   0.00020            * math.sin (q+2.0*l) 
    ps = ps-   0.00020            * math.sin (2.0*q+l) 
    ps = ps+   0.00020            * math.sin (3.0*l) 
    ps = ps+   0.00020            * math.sin (2.0*q+d+2.0*f) 
    ps = ps+   0.00010            * math.sin (2.0*q-l) 
    ps = ps-   0.00010            * math.sin (l-4.0*d) 
    ps = ps+   0.00010            * math.sin (2.0*(q+d+f-l)) 
    ps = ps-   0.00020            * math.sin (2.0*q+4.0*d+2.0*f-l) 
    ps = ps-   0.00010            * math.sin (2.0*l-4.0*d) 
    ps = ps+   0.00010            * math.sin (2.0*q-2.0*d+2.0*f+m+l) 
    ps = ps-   0.00010            * math.sin (q+2.0*d+2.0*f+l) 
    ps = ps-   0.00010            * math.sin (2.0*q+4.0*d+2.0*f-2.0*l) 
    ps = ps+   0.00010            * math.sin (2.0*q+4.0*f-l) 
    ps = ps+   0.00010            * math.sin (l-m-2.0*d) 
    ps = ps+   0.00010            * math.sin (q-2.0*d+2.0*f+2.0*l) 
    ps = ps-   0.00010            * math.sin (2.0*(q+d+f+l)) 
    ps = ps-   0.00010            * math.sin (q+2.0*d+l) 
    ps = ps+   0.00010            * math.sin (2.0*q-2.0*d+4.0*f) 
    ps = ps+   0.00010            * math.sin (2.0*q-2.0*d+2.0*f+3.0*l) 
    ps = ps-   0.00010            * math.sin (l+2.0*f-2.0*d) 
    ps = ps+   0.00010            * math.sin (q+2.0*f+m) 
    ps = ps+   0.00010            * math.sin (q+2.0*d-m-l) 
    ps = ps-   0.00010            * math.sin (q-2.0*f) 
    ps = ps-   0.00010            * math.sin (2.0*q-d+2.0*f) 
    ps = ps-   0.00010            * math.sin (2.0*d+m) 
    ps = ps-   0.00010            * math.sin (l-2.0*f-2.0*d) 
    ps = ps-   0.00010            * math.sin (q+2.0*f-m) 
    ps = ps-   0.00010            * math.sin (q-2.0*d+m+l) 
    ps = ps-   0.00010            * math.sin (l-2.0*f+2.0*d) 
    ps = ps+   0.00010            * math.sin (2.0*(l+d)) 
    ps = ps-   0.00010            * math.sin (2.0*q+4.0*d+2.0*f) 
    ps = ps+   0.00010            * math.sin (d+m) 
    
    s0 = sm+(pl+ps)/15.0* math.cos(e) 

    s_hour = math.floor(s0/3600) 
    s_min = math.floor((s0-s_hour*3600)/60) 
    s_sec = math.floor((s0-s_hour*3600-s_min*60)*10000)/10000
    
    return (s_hour, s_min, s_sec)




