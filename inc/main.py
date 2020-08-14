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

    print("INCREMENTAL COMPILATION EXPERIMENTATION")
    expdsl_file = sys.argv[1]
    kernel_path = sys.argv[2].split('/')
    print("* Exp spec file: {}".format(expdsl_file))
    print("* Kernel path: {}".format(kernel_path))
    print("- Directory for compilation from scratch: {}".format(SCRATCH_DIR))
    os.system("mkdir {}".format(SCRATCH_DIR))
    print("- Parsing {} ...".format(expdsl_file))
    sym, chains = expdsl.parse_file(expdsl_file)

    rep = lambda x: sym[x] if (x in sym) else x
    chains = list(map(lambda l: list(map(rep, l)), chains))
    main_kernel = Kernel(kernel_path)
    print("- Clean {}".format(kernel_path))
    main_kernel.clean()

    tmp_l = kernel_path.split('/')
    if tmp_l[-1].strip() == '/':
        tmp_l = tmp_l[:-1]
    kernel_name = tmp_l[-1]

    dir_sym = dict()
    compiled_config = set()
    print("- Compilation exp start")
    for i, chain in enumerate(chains):
        incremental_dir = "incremental{}".format(i)
        print("- Creating incremental dir: {}".format(incremental_dir))
        os.system("mkdir {}".format(incremental_dir))
        # os.system("cp -rp {} {}".format(main_kernel.get_dir_name(),
        #                                incremental_dir))
        # incremental_kernel = Kernel("{}/{}".format(incremental_dir,
        #                                            kernel_name))
        incremental_kernel = None
        with open("{}/chain".format(incremental_dir), 'w') as ifile:
            ifile.write("\n".join(chain))

        for j, config in enumerate(chain):
            scratch_kernel = None
            if config not in compiled_config:
                # COMPILE FROM SCRATCH
                print("- Current config was not already compiled")
                print("- COMPILATION FROM SCRATCH")
                dest = "{}/".format(SCRATCH_DIR)
                if config in sym.values():
                    for k in sym:
                        if sym[k] == config:
                            dest += k
                else:
                    dest += "config{}-{}".format(i, j)
                os.system("mkdir {}".format(dest))
                os.system("cp -rp {} {}".format(main_kernel.get_dir_name(),
                                                dest))
                dir_sym[config] = "{}/{}"\
                                        .format(dest, kernel_name)
                print("- Target dir: {}".format(dir_sym[config]))
                scratch_kernel = Kernel(dir_sym[config])
                print("- Compiling...")
                scratch_kernel.compile(config=config, time=True)
                print("- Compilation done")
                compiled_config.add(config)
                # Check
                print("- CHECKING")
                with open("{}/compile_time"\
                          .format(scratch_kernel.get_dir_name()), "w")\
                          as time_file:
                    time_file.write("{}"\
                                    .format(scratch_kernel.get_compile_time()))
                scratch_checker = Checker(scratch_kernel, verbose=True)
                scratch_checker.builtin()
            else:               # if config not in compiled_config
                scratch_kernel = Kernel(dir_sym[config])
            # At this point, a kernel should be compiled
            if j == 0:
                scratch_kernel.save(incremental_dir)
            else:               # /!\
                # INCREMENTAL COMPILATION
                # Compiling the first configuration of an incremental
                # configuration is the same as compiling from sratch
                # this config
                print("- INCREMENTAL COMPILATION")
                print("- Target dir: {}/{}"\
                      .format(incremental_dir, kernel_name))
                incremental_kernel = Kernel("{}/{}"\
                                            .format(incremental_dir,
                                                    kernel_name))
                print("- Compiling...")
                incremental_kernel.compile(config=config, time=True)
                print("- Compilation done")
                # Check
                print("- CHECKING")
                incremental_checker = Checker(incremental_kernel,
                                              verbose=True)
                incremental_checker.builtin()
                incremental_checker.dir_full_timestamp()
                with open("{}/compile_time"\
                          .format(incremental_kernel.get_dir_name()), 'w')\
                          as time_file:
                    time_file.write("{}".format(
                        incremental_kernel.get_compile_time()))
                incremental_kernel.save("{}/{}"\
                                        .format(incremental_dir, config))
if __name__ == "__main__":
    main()
