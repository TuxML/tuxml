"""Incremental compilation experimentation
"""
import os
import sys
import expdsl
from kernel import Kernel, Checker


SCRATCH_DIR = "scratch"


def main():
    """Main function"""

    if len(sys.argv) != 3:
        print(\
"""Usage:
\tpython inc_exp <filename> <kernel>
where
\t<filename> is the file containing the configs to compile
\t<kernel> is a path to the kernel source code
""")
        sys.exit()

    expdsl_file = sys.argv[1]
    kernel_path = sys.argv[2]

    os.system("mkdir {}".format(SCRATCH_DIR))
    sym, chains = expdsl.parse_file(expdsl_file)

    rep = lambda x: sym[x] if (x in sym) else x
    chains = list(map(lambda l: list(map(rep, l)), chains))
    main_kernel = Kernel(kernel_path)
    main_kernel.clean()

    tmp_l = kernel_path.split('/')
    if tmp_l[-1].strip() == '/':
        tmp_l = tmp_l[:-1]
    kernel_name = tmp_l[-1]

    dir_sym = dict()
    for i, chain in enumerate(chains):
        incremental_dir = "incremental{}".format(i)
        os.system("mkdir {}".format(incremental_dir))
        os.system("cp -r {} {}".format(main_kernel.get_dir_name(),
                                       incremental_dir))
        incremental_kernel = Kernel("{}/{}".format(incremental_dir,
                                                   kernel_name))
        with open("{}/chain".format(incremental_dir), 'w') as ifile:
            ifile.write("\n".join(chain))

        for j, config in enumerate(chain):
            # COMPIL FROM SCRATCH IF NEEDED
            scratch_kernel = None
            if not already_compiled(SCRATCH_DIR, config):
                dest = "{}/".format(SCRATCH_DIR)
                if config in sym.values():
                    for k in sym:
                        if sym[k] == config:
                            dest += k
                else:
                    dest += "config{}-{}".format(i, j)
                dir_sym[config] = dest
                main_kernel.compile(config=config, dest=dest, time=True)
                scratch_kernel = Kernel(dest)
                # Check
                with open("{}/compile_time"\
                          .format(scratch_kernel.get_dir_name()), "w")\
                          as time_file:
                    time_file.write("{}".format(main_kernel.get_compile_time()))
                scratch_checker = Checker(scratch_kernel, verbose=True)
                scratch_checker.builtin()
                main_kernel.clean()
            else:
                scratch_kernel = Kernel(dir_sym[config])
            # INCREMENTAL COMPILATION
            incremental_kernel.compile(config=config, time=True)
            # Check
            incremental_checker = Checker(incremental_kernel, verbose=True)
            incremental_checker.builtin()
            incremental_checker.dir_full_timestamp()
            if j > 0:
                with open("{}/compile_time"\
                          .format(incremental_kernel.get_dir_name()), 'w')\
                     as time_file:
                    time_file.write("{}".format(
                        incremental_kernel.get_compile_time()))
            if j > 0:
                assert scratch_kernel is not None, "SCRATCH KERNEL is None"
                incremental_checker.bloat_o_meter(scratch_kernel)
            incremental_kernel.save("{}/config{}".format(incremental_dir, j))


if __name__ == "__main__":
    main()
