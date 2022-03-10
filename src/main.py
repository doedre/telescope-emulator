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
    telescope = tcd.Telescope()
    iface = tin.Interface()
    iface.moveButtonClicked.connect(telescope.set_star_coords)
    iface.parkButtonClicked.connect(telescope.park_telescope)

    lock_coord = thr.Lock()
    proc_coord = thr.Thread(target=telescope.running, args=(lock_coord,))
    worker_coord = thr.Thread(target=telescope.worker, args=(lock_coord,))

    # Start workers
    proc_coord.start()
    worker_coord.start()

    # Start interface
    iface.show()
    app.exec()

    # Join threads and exit
    telescope.stop_thread(lock_coord)
    proc_coord.join()
    worker_coord.join()

if __name__ == '__main__':
    sys.exit(main())
