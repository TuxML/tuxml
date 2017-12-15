import sys
import time
import math
import os

# ===== GLOBALS =====
# "/std_{}.log".format(math.ceil(time.time()))
# "/err_{}.log".format(math.ceil(time.time()))

PATH = ""
LOG_DIR = "/logs"
STD_LOG_FILE = LOG_DIR + "/std.log"
ERR_LOG_FILE = LOG_DIR + "/err.log"
VERBOSE = False
OUTPUT = open(os.devnull, 'w')
NB_CORES = 1
