import os
import subprocess
from pathlib import Path
LOGFILE = "stderr.output"
data_dir = "data"


"""
CHECKERS
"""

def compile(kernel_path, config, dest):
    """Compiles a kernel in dest
    
    :param kernel_path: path to the kernel to compile
    :type kernel_path: str
    :param config: path to a configuration
    :type config: str
    :param dest: directory to compile the kernel in
    :type dest: str
    """
    subprocess.run(args="make -C {} O={} {}".format(kernel_path, dest, config),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=LOGFILE,
                check=True)
    subprocess.run(args="make -C {} O={} -j4".format(kernel_path, dest),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=LOGFILE,
                check=True)


def inc_building(kernel_path, configs):
    """Compiles incrementally some kernel according
    to the given rules in configs
    
    :param kernel_path: path to the kernel
    :type kernel_path: str
    :param configs: list of rules 
    :type configs: list(str)
    """
    dest = "kernel0"
    compile(kernel_path, configs[0], dest)
    check(dest)
    config = configs[1:]
    for i, config in enumerate(configs, 1):
        # incremental
        compile(kernel_path, config, dest)
        check(dest)
        # from scratch
        from_scratch = "{}-scratch-{}".format(config, i)
        compile(kernel_path, config, from_scratch)
        check(from_scratch)
        bloat_o_meter_compare(kernel_path,
                              dest, from_scratch,
                              "{}/bloat-{}".format(data_dir, i))
    

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


def vmlinux_check(kernel, outputfn):
    """Checks for the size of vmlinux
    """
    subprocess.run(args="du -sh {}/vmlinux > {}".format(kernel, outputfn),
                   shell=True)


def bloat_o_meter_compare(kernel_src, kernel_inc, kernel_scratch, outputfn):
    """
    """
    subprocess.run(args='{}/scripts/bloat-o-meter {}/vmlinux\
    {}/vmlinux > {}'.format(kernel_src,
                            kernel_scratch,
                            kernel_inc, outputfn),
                   shell=True)


checkers = [builtin_check, vmlinux_check]
def check(dest):
    """
    """
    for checker in checkers:
        checker(dest, "{}/{}-{}".format(data_dir, checker.__name__, dest))
