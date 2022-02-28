import argparse
import time
import sys
sys.path.append("../src/")
# Write your imports from `src/` folder below
import logger as log
from telescope import Telescope, Star, calculate_s, dms_to_d, d_to_dms
from siderealtimeS0 import calculate_S0

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple telescope emulator")
    parser.add_argument("--debug", action="store_true", help="Stores additional debug info into log file")
    parser.add_argument("--log-path", default="log.txt", help="Path to the log file. Default: 'log.txt'")

    args = vars(parser.parse_args())
    is_debug = args.pop("debug")
    log_path = args["log_path"]

    # Setup logger
    if is_debug == True:
        log.set_debug_level()
    log.set_log_path(log_path)

    #
    # Write your tests below
    #
    
    #создание экземпляра класса Telescope и Star
    t = Telescope()
    star = Star(70, 40)
    log.debug("start telescope position: h = {0} deg, A = {1} deg ".format(t.alt, t.az))
    log.debug("star coord: RA = {0} deg, DEC = {1} deg ".format(star.ra, star.dec))
    
    #вычисление S0 на теущую дату
    date = time.localtime(time.time())
    S0 = calculate_S0(date)
    log.debug("sidereal time at greenwich midnight: S0 = {0}h {1}m {2}s".format(S0[0], S0[1], S0[2]))
    
    #вычисление текущего звездного времени и (h, A) звезды
    date = time.localtime(time.time())
    S0 = dms_to_d(S0[0], S0[1], S0[2])
    T = dms_to_d(date.tm_hour, date.tm_min, date.tm_sec)
    stime = calculate_s(S0, T)
    stime_h, stime_m, stime_s = d_to_dms(stime)
    log.debug("sidereal time at T = {0}h {1}m {2}s is: s = {3}h {4}m {5}s".format(date.tm_hour, date.tm_min, date.tm_sec, stime_h, stime_m, stime_s))
    h_star, A_star = star.eq_to_hor(stime)
    log.debug("star coord: h = {0} deg, A = {1} deg ".format(h_star, A_star))
    
    #наведение на звезду
    date = time.localtime(time.time())
    t.move_to_star(star, date)
    log.debug("telescope coord: h = {0} deg, A = {1} deg. star coord: h = {2} deg, A = {3} deg".format(t.alt, t.az, star.alt, star.az))
    
    #ведение телескопа с момента времени date в течение 5 сек
    date = time.localtime(time.time())
    t.guidance(star, date, 5)
    log.debug("telescope coord: h = {0} deg, A = {1} deg. star coord: h = {2} deg, A = {3} deg".format(t.alt, t.az, star.alt, star.az))
    
    #парковка телескопа
    t.parking()
    log.debug("telescope coord: h = {0} deg, A = {1} deg".format(t.alt, t.az))
    
    #смена режима
    t.change_mode()
    


if __name__ == '__main__':
    sys.exit(main())