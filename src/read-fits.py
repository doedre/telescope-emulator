from astropy.io import fits
from datetime import datetime
import numpy as np
import time
from siderealtimeS0 import  calculate_S0
from telescope import Star, calculate_s, dms_to_d

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
    name = file_type + mode + '.fts'
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
    name = 's' + conuntfile + '.fts'
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
    hdu.header['A'] = star.
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



    
    
    
    
    
    
    
    
    
