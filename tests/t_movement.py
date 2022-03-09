#!/usr/bin/python3

import multiprocessing as mp
import argparse
import sys
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

    #
    # Write your tests below
    #

    lock = mp.Lock()
    tel = tcd.Telescope()
    star = tcd.Star(20, 30)
    log.info("Initializing")
    proc = mp.Process(target=tel.running, args=(lock,))
    proc.start()
    for i in range(3):
        log.debug("Iteration number {0}".format(i))
        tel.cont(lock, 20, 30)

    proc.join()

if __name__ == '__main__':
    sys.exit(main())
