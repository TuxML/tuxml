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
            self._ctime = timeit.timeit(stmt=ccmd, setup="import os", number=1)
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
