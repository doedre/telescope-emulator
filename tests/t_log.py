import sys
sys.path.append("../src/")
import logger as log

# Example for log usage

log.debug("try to log stuff {0}".format(10))
log.info("here comes the info")
log.warn("be cautios")
