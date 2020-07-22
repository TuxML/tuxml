"""Incremental compilation experimentation
"""
import os
import sys
import subprocess


def main():
    if len(sys.argv) != 3:
        print(\
"""Usage:
\tpython inc_expt <filename> <kernel>
where
\t<filename> is the file containing the configs to compile
\t<kernel> is a path to the kernel source code
""")
        sys.exit()
    file = sys.argv[1]
    kernel_path = sys.argv[2]
    os.system("mkdir inc scratch && cp -r {} inc/".format(kernel_path))
    inc_launcher(kernel_path, file)


def inc_launcher(kernel_path, file):
    rules = []
    with open(file, 'r') as f:
        rules = [l.strip('\n') for l in f.readlines()]
    for rule in rules:
        inc_build(kernel_path, [c.strip() for c in rule.split('->')])


def inc_build(kernel_path, configs):
    tmp_l = kernel_path.split('/')
    if tmp_l[-1].strip() == "/":
        tmp_l = tmp_l[:-1]
    kernel_name = tmp_l[-1]
    kernel_for_scratch = "scratch/{}".format(kernel_name)
    kernel_for_inc = "inc/{}".format(kernel_name)
    for config in configs:
        compiled_from_scratch = "scratch/{}".format(config)
        # scratch
        os.system("cp {} {}".format(config, kernel_for_scratch))
        os.system("make -C {} O=../{}"\
                  .format(kernel_for_scratch, config))
        os.system("make -C {} mrpropper".format(kernel_for_scratch))
        # incremental
        os.system("cp {} {}".format(config, kernel_for_inc))
        os.system("make -C {}".format(kernel_for_inc))
        # check
        os.system("cp {}/vmlinux {}/vmlinux.inc"\
                  .format(kernel_for_inc, compiled_from_scratch))
        # BLOAT-O-METER
        # bloat-o-meter vmlinux vmlinux.inc
        os.system(
            "{}/scripts/bloat-o-meter {}/vmlinux {}/vmlinux.inc > {}/bloatsi"\
                  .format(kernel_for_scratch, compiled_from_scratch,
                          compiled_from_scratch, compiled_from_scratch))
        # bloat-o-meter vmlinux.inc vmlinux
        os.system(
            "{}/scripts/bloat-o-meter {}/vmlinux.inc {}/vmlinux > {}/bloatis"\
                  .format(kernel_for_scratch, compiled_from_scratch,
                          compiled_from_scratch, compiled_from_scratch))
        # VMSIZE
        os.system('echo "scratch" >> {}/vmsizecompare'\
                  .format(compiled_from_scratch))
        os.system("echo $(du -sh vmlinux) >> {}/vmsizecompare"\
                  .format(compiled_from_scratch))
        os.system('echo "incremental" >> {}/vmsizecompare'\
                  .format(compiled_from_scratch))
        os.system("echo $(du -sh vmlinux.inc) >> {}/vmsizecompare"\
                  .format(compiled_from_scratch))
        # BUILT-IN
        subprocess.run(
            args=\
            'find {} -name "built-in.o" | xargs size | sort -n -r -k 4\
            > {}/builtinsize-scratch'\
            .format(compiled_from_scratch, compiled_from_scratch),
            shell=True, check=True)
        if os.stat("builtinsize-scratch").st_size == 0:
            subprocess.run(
                args='find {} -name "built-in.a" | xargs size | sort -n -r -k 4\
                > {}/builtinsize-scratch'\
                .format(compiled_from_scratch, compiled_from_scratch),
                shell=True, check=True)
        subprocess.run(
            args=\
            'find {} -name "built-in.o" | xargs size | sort -n -r -k 4\
            > {}/builtinsize-inc'.format(kernel_for_inc, compiled_from_scratch),
            shell=True, check=True)
        if os.stat("builtinsize-scratch").st_size == 0:
            subprocess.run(
                args='find {} -name "built-in.a" | xargs size | sort -n -r -k 4\
                > {}/builtinsize-inc'\
                .format(kernel_for_inc, compiled_from_scratch),
                shell=True, check=True)


if __name__ == "__main__":
    main()
