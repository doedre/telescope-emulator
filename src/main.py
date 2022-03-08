#!/usr/bin/env python3

import argparse
import sys

import logging as log

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

if __name__ == '__main__':
    sys.exit(main())
