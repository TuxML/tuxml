"""Incremental compilation experimentation
"""
import os
import sys
import timeit

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
    # kernel_for_scratch = "scratch/{}".format(kernel_name)
    kernel_for_scratch = kernel_path
    kernel_for_inc = "inc/{}".format(kernel_name)
    for config in configs:
        compiled_from_scratch = "scratch/{}".format(config)
        # scratch
        print("=> Compiling the kernel with {} from scratch".format(config))
        os.system("mkdir {}".format(compiled_from_scratch))
        os.system("cp {} {}/.config".format(config, compiled_from_scratch))
        print("Compiling from scratch {}".format(config))
        cmd_scratch = 'os.system("make -C {} O=../{} -j4")'\
            .format(kernel_for_scratch, compiled_from_scratch)
        scratch_time = timeit.timeit(stmt=cmd_scratch,
                                     setup="import os", number=1)
        os.system("make -C {} mrproper".format(kernel_for_scratch))
        print("[OK] Compilation done")
        # incremental
        print("=> Incremental compilation")
        os.system("cp {} {}/.config".format(config, kernel_for_inc))
        cmd_incremental = 'os.system("make -C {} -j4")'.format(kernel_for_inc)
        incremental_time = timeit.timeit(stmt=cmd_incremental,
                                         setup="import os", number=1)
        print("[OK] Compilation done")
        # copy of the folder
        os.system("mkdir inc/{} && cp -r {} inc/{}"\
                  .format(config, kernel_for_inc, config))
        # Writing compilation time in a file
        with open("{}/comp_time".format(compiled_from_scratch), 'w') as tfile:
            tfile.write(
                "scratch: {}\nincremental: {}"\
                .format(scratch_time, incremental_time))
        # check
        print("=> Checking...")
        os.system("cp {}/vmlinux {}/vmlinux.inc"\
                  .format(kernel_for_inc, compiled_from_scratch))
        # BLOAT-O-METER
        # bloat-o-meter vmlinux vmlinux.inc
        print("\t-> Bloat-o-meter check")
        print("\t\t* vmlinux | vmlinux.inc")
        os.system(
            "{}/scripts/bloat-o-meter {}/vmlinux {}/vmlinux.inc > {}/bloatsi"\
                  .format(kernel_for_scratch, compiled_from_scratch,
                          compiled_from_scratch, compiled_from_scratch))
        # bloat-o-meter vmlinux.inc vmlinux
        print("\t\t* vmlinux.inc | vmlinux")
        os.system(
            "{}/scripts/bloat-o-meter {}/vmlinux.inc {}/vmlinux > {}/bloatis"\
                  .format(kernel_for_scratch, compiled_from_scratch,
                          compiled_from_scratch, compiled_from_scratch))
        print("[OK] Bloat-o-meter done")
        # VMSIZE
        print("\t-> Vmlinux size check")
        with open("vmsizecompare", 'w') as vmf:
            vmf.write("scratch: {}\n"\
                      .format(os.path.getsize("{}/vmsizecompare"\
                                              .format(compiled_from_scratch))))
            vmf.write("incremental: {}\n"\
                      .format(os.path.getsize("{}/vmlinux"\
                                              .format(compiled_from_scratch))))
        # Old version using command line
        # ==============================
        # os.system('echo "scratch" >> {}/vmsizecompare'\
        #           .format(compiled_from_scratch))
        # os.system("echo $(du -sh {}/vmlinux) >> {}/vmsizecompare"\
        #           .format(compiled_from_scratch, compiled_from_scratch))
        # os.system('echo "incremental" >> {}/vmsizecompare'\
        #           .format(compiled_from_scratch))
        # os.system("echo $(du -sh {}/vmlinux.inc) >> {}/vmsizecompare"\
        #           .format(compiled_from_scratch, compiled_from_scratch))

        print("[OK] Vmlinux size check done")
        # BUILT-IN
        print("\t-> Check for built-in.o")
        os.system(
            'find {} -name "built-in.o" | xargs size | sort -n -r -k 4\
            > {}/builtinsize-scratch'\
                  .format(compiled_from_scratch, compiled_from_scratch))
        if os.stat("{}/builtinsize-scratch".format(compiled_from_scratch))\
             .st_size == 0:
            print("\t\t/!\\ No built-in.o")
            print("\t\t* Checking for built-in.a")
            os.system(
                'find {} -name "built-in.a" | xargs size | sort -n -r -k 4\
                > {}/builtinsize-scratch'\
                .format(compiled_from_scratch, compiled_from_scratch))
            print("\t\t[OK] built-in.a check done")
        os.system(
            'find {} -name "built-in.o" | xargs size | sort -n -r -k 4\
            > {}/builtinsize-inc'.format(kernel_for_inc, compiled_from_scratch))
        if os.stat("{}/builtinsize-scratch".format(compiled_from_scratch))\
                   .st_size == 0:
            print("\t\t/!\\ No built-in.o")
            print("\t\t* Checking for built-in.a")
            os.system(
                'find {} -name "built-in.a" | xargs size | sort -n -r -k 4\
                > {}/builtinsize-inc'\
                .format(kernel_for_inc, compiled_from_scratch))
            print("\t\t[OK] built-in.a check done")
        # Check timestamp of each files of kernel_for_inc
        print("[OK] Check done")


if __name__ == "__main__":
    main()
