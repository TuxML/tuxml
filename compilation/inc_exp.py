import os
import subprocess
from pathlib import Path
LOGFILE = "stderr.output"
data_dir = "data"


"""
CHECKERS
"""

def builtin_check(kernel, outputfn):
    """Checks for the built-in files
    """
    subprocess.run(args='find {} -name "built-in.o" | xargs size |\
    sort -n -r -k 4 > {}'.format(kernel, outputfn),
                   shell=True)
    if os.stat("output").st_size == 0:
        print("*/built-in.o do not exist, checking for */built-in.a")
        subprocess.run(args='find {} -name "built-in.a" | xargs size |\
        sort -n -r -k 4 > {}'.format(kernel, outputfn),
                    shell=True)
