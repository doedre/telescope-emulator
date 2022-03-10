#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
import threading as thr
import os

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QApplication

import te_coords as tcd
import te_interface as tin
import te_fits as tft
import logger as log

def main():
    app = QApplication(sys.argv)

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

    # Initialize workers
    log.info("Initializing")
    lock_coord = thr.Lock()
    lock_plot = thr.Lock()

    telescope = tcd.Telescope()
    iface = tin.Interface()
    fits = tft.FitsWorker(lock_plot)
    iface.moveButtonClicked.connect(telescope.set_star_coords)
    iface.parkButtonClicked.connect(telescope.park_telescope)
    iface.startButtonClicked.connect(fits.set_fits_path)

    proc_coord = thr.Thread(target=telescope.running, args=(lock_coord,))
    worker_coord = thr.Thread(target=telescope.worker, args=(lock_coord,))
    proc_plot = thr.Thread(target=fits.running, args=())

    # Start workers
    proc_coord.start()
    worker_coord.start()
    proc_plot.start()

    # Start interface
    iface.show()
    app.exec()

    # Join threads and exit
    telescope.stop_thread(lock_coord)
    fits.stop_thread()
    proc_coord.join()
    worker_coord.join()
    proc_plot.join()

if __name__ == '__main__':
    sys.exit(main())
