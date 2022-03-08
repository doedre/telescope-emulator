import argparse
import sys
sys.path.append("../src/")
import logger as log

def func_module():
    log.debug("debug in another function in another module")
    log.info("info in another function in another module")
    log.warn("warn in another function in another module")
