#!/usr/bin/env python3

import multiprocessing as mp
import argparse
import sys
sys.path.append("../src/")
# Write your imports from `src/` folder below
import logger as log
import test_module

def func():
    log.debug("debug in another function")
    log.info("info in another function")
    log.warn("warn in another function")

def func_thread():
    log.debug("debug in another function in another thread")
    log.info("info in another function in another thread")
    log.warn("warn in another function in another thread")

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

    # Try logger functions
    log.debug("debug in main")
    log.info("info in main")
    log.warn("warn in main")

    func()
    test_module.func_module()
    proc = mp.Process(target=func_thread, args=())
    proc.start()
    proc.join()

    proc = mp.Process(target=test_module.func_module, args=())
    proc.start()
    proc.join()

if __name__ == '__main__':
    sys.exit(main())
