#!/usr/bin/python3

import threading as thr
import argparse
import sys
import time
sys.path.append("../src/")
# Write your imports from `src/` folder below
import te_coords as tcd
import logger as log

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
        time.sleep(1)

    tel.stop_thread(lock)

    proc.join()

if __name__ == '__main__':
    sys.exit(main())
