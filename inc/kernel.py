"""This file contains a class that represents a Kernel with the
minimum task possible with a kernel:
* generate a configuration (randconfig, tinyconfig);
* compile a kernel (time it or not);
* clean the kernel directory (using mrproper);
* save the current state of the directory.

This class is minimal: other check possible like size, built-in,
etc... can be from the outside of the class so no need to add them to
this class.

.. notes:: can be improved by writing syscalls fully in Python instead
of using ``os.system`` each time.

This file contains also a Checker class. This class retrieve
information from a Linux kernel directory.

The aim of this file is to separate the kernel and the checkers and
let users to write their own checker (not hide them) and check a
Kernel using a simple method.

"""


import os
import timeit


class Kernel:
    """Class that represent a Linux kernel directory with the minimum task
    possible: generate a configuration, compile, save the state of the
    directory and clean it. It is possible to time a compilation. More
    information about a compilation can be retrieve from outside hence
    no need to add it to this class.

    :param direc: path to the Linux kernel directory
    :type direc: string
    :raise: NotADirectoryError
    """

    def __init__(self, direc):
        self._dir = ""
        self._ctime = 0
        if os.path.exists(direc):
            self._dir = direc
        else:
            raise NotADirectoryError("{} is not a directory".format(direc))

    def randconfig(self):
        """Generates a random configuration using Linux kernel's
        ``randconfig``

        .. notes:: It does only a generation. It does not compile the
        kernel.
        """
        os.system("make -C {} randconfig".format(self._dir))

    def tinyconfig(self):
        """Generates a tiny configuration using Linux kernel's ``tinyconfig``
        """
        os.system("make -C {} tinyconfig".format(self._dir))

    def compile(self, config=None, dest=None, time=False):
        """Compile a kernel.

        :param config: path to a configuration to compile the kernel\
        with. Default: ``None``.
        :type config: str
        :param dest: path to a directory to compile the kernel into.\
        If ``dest`` is ``None``, the kernel will be compiled in its\
        own directory. Default: ``None``.
        :type dest: str

        .. notes:: Be careful, the path should be relative to the
        Linux kernel.

        :param time: ``True`` if the compilation should be\
        timed. ``False`` otherwise.
        :type time: bool
        """
        ccmd = "make -C {}".format(self._dir)
        if config is not None:
            os.system("cp {} {}/.config".format(config, self._dir))
        if dest is not None:
            ccmd += " O={}".format(dest)
        ccmd += " -j4"
        if time:
            self._ctime = timeit.timeit(stmt='os.system("{}")'.format(ccmd),
                                        setup="import os", number=1)
        else:
            os.system(ccmd)

    def clean(self):
        """Clean directory with ``mrproper``
        """
        os.system("make -C {} mrproper".format(self._dir))

    def save(self, save_dir):
        """Save the directory to another directory

        :param save_dir: path to a directory to save the current one\
        in
        :type save_dir: str
        """
        os.system("cp -r {} {}".format(self._dir, save_dir))

    def get_compile_time(self):
        """Gives compile time of previous compilation.

        .. warning:: ``0`` if the kernel was not compiled yet.

        """
        return self._ctime

    def get_dir_name(self):
        """Gives the name of the directory that contains the Kernel's
        source

        """
        return self._dir


class Checker:
    """Checker of kernel's properties

    :param ker_obj: a Linux kernel
    :type ker_obj: kernel.Kernel
    :param verbose: ``True`` to make the checker verbose. ``False``\
    otherwise
    :type verbose: bool
    """

    def __init__(self, ker_obj, verbose=False):
        if not isinstance(ker_obj, Kernel):
            raise TypeError("Parameter should be of type Kernel")
        self._kernel = ker_obj
        self._verbose = verbose

    def check(self):
        """Launch checks on the kernel dir"""
        pass

    def builtin(self):
        """Checks for every built-in.(a|o) of the directory recursively and
        get their size. Write the result in a file.
        """
        res_file = "{}/builtins.size".format(self._kernel.get_dir_name())
        if self._verbose:
            print("[c] CHECKER: BULT-IN...")
            print("[i] Checking for built-in.o")
        os.system(
            'find {} -name "built-in.o" | xargs size | sort -n -r -k 4\
            > {}'.format(self._kernel.get_dir_name(), res_file))
        if os.stat(res_file).st_size == 0:
            if self._verbose:
                print("\t[!] No built-in.o")
                print("[i] Checking for built-in.a")
            os.system(
                'find {} -name "built-in.a" | xargs size | sort -n -r -k 4\
                > {}'.format(self._kernel.get_dir_name(), res_file))
        if self._verbose:
            print("[x] CHECKER: BUILT-IN <DONE>")

    def vmlinux_size(self):
        """Vmlinux size
        :return: size of vmlinux
        :rtype: int
        """
        if self._verbose:
            print("[c] CHECKER: VMLINUX SIZE")
        vmlinux = "{}/vmlinux".format(self._kernel.get_dir_name())
        if self._verbose:
            print("[x] CHECKER: VMLINUX SIZE <DONE>")
        return os.path.getsize(vmlinux)

    def dir_full_timestamp(self):
        """Write into a file the timestamp of each file of the directory"""
        if self._verbose:
            print("[c] CHECKER: DIR TIMESTAMP")
        res_file = "{}/dir.tmstp".format(self._kernel.get_dir_name())
        os.system("find {} -printf '%C@ %p\n' > {}"\
                  .format(self._kernel.get_dir_name(), res_file))
        if self._verbose:
            print("[x] CHECKER: DIR TIMESTAMP <DONE>")

    def bloat_o_meter(self, other):
        """Bloat_o_meter of two vmlinux
        :param other: other kernel object
        :type other: Kernel
        """
        if self._verbose:
            print("[c] CHECKER: BLOAT-O-METER")
        this_vmlinux = "{}/vmlinux".format(self._kernel.get_dir_name())
        other_vmlinux = "{}/vmlinux".format(other.get_compile_time())
        res_file = "{}/bloatto".format(self._kernel.get_dir_name())
        cmd = "{}/scripts {} {} > {}".format(self._kernel.get_dir_name(),
                                             this_vmlinux, other_vmlinux,
                                             res_file)
        os.system(cmd)
        if self._verbose:
            print("[x] CHECKER: BLOAT-O-METER <DONE>")
