#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess
import bz2
import json

from compilation.environment import get_environment_details, print_environment_details
from compilation.configuration import create_configuration, print_configuration
from compilation.package_manager import PackageManager
from compilation.logger import Logger, COLOR_SUCCESS
from compilation.compiler import Compiler
from compilation.boot_checker import BootChecker
from compilation.database_management import fetch_connection_to_database, insert_if_not_exist_and_fetch_hardware, insert_if_not_exist_and_fetch_software, insert_and_fetch_compilation, insert_incrementals_compilation, insert_boot_result, insert_sizes
import compilation.settings as settings


## parser
# @author PICARD Michaël
# @version 1
# @brief Parse the commandline and return the parsed argument.
def parser():
    """Parse the commandline argument

    :return: object in which each attribute is one argument and its\
    value. Check\
    `argparse <https://docs.python.org/3/library/argparse.html>`_\
    for more info.
    :rtype: `argparse.Namespace`_
    
    .. _argparse.Namespace: https://docs.python.org/3.8/library/argparse.html#argparse.Namespace
    """    
    parser = argparse.ArgumentParser(
        description=""  # TODO: Fill the description
    )
    parser.add_argument(
        "incremental",
        type=int,
        help="Optional. Provide the number of additional incremental "
             "compilation. Have to be 0 or over.",
        nargs='?',
        default=0
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Prevent printing on standard output when compiling."
    )
    parser.add_argument(
        "--tiny",
        action="store_true",
        help="Use Linux tiny configuration. Incompatible with --config "
             "argument."
    )
    parser.add_argument(
        "--config",
        help="Give a path to specific configuration file. Incompatible with "
             "--tiny argument."
    )
    parser.add_argument(
        "--cpu_cores",
        help="Give the number of cpu cores to use. Default to 0, which mean all"
             " the cores.",
        default=0
    )
    parser.add_argument(
        "--boot",
        action="store_true",
        help="Optional. Try to boot the kernel after compilation if the compilation "
             "has been successful."
    )
    parser.add_argument(
        "--check_size",
        action="store_true",
        help="Optional. Compute additional size measurements on the kernel and send "
             "the results to the 'sizes' table (can be heavy)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="create a json which has importants informations."
    )
    parser.add_argument(
        "--mount_host_dev",
        action="store_true",
        help="create a json which has importants informations."
    )
    
    return parser.parse_args()


## create_logger
# @author PICARD Michaël
# @version 1
# @brief Create the logger object and return it.
def create_logger(silent):
    """Creates an object logger

    :return: the created object logger
    :rtype: `Logger`_

    .. _Logger: logger.html

    """
    return Logger(
        settings.OUTPUT_FILE,
        settings.STDOUT_FILE,
        settings.STDERR_FILE,
        settings.BOOT_FILE,
        silent
    )


## retrieve_and_display_environment
# @author PICARD Michaël
# @version 1
# @brief Retrieve and display the environment dictionary.
def retrieve_and_display_environment(logger):
    """Retrieve and display the environment details

    :param logger: the logger
    :type logger: `Logger`_
    :return: the environment
    :rtype: dict
    """
    logger.timed_print_output("Getting environment details.")
    environment = get_environment_details()
    print_environment_details(environment, logger.print_output)
    return environment


## retrieve_and_display_configuration
# @author PICARD Michaël
# @version 1
# @brief Retrieve and display the configuration dictionary.
def retrieve_and_display_configuration(logger, args):
    """Retrieve and display configuration details (of the machine)
    
    :param logger: the logger
    :type logger: `Logger`_
    :param args: parsed arguments
    :type args: `argparse.Namespace`_
    :return: configuration info
    :rtype: dict
    """
    logger.timed_print_output("Getting configuration details.")
    configuration = create_configuration(int(args.cpu_cores), args.incremental != 0)
    print_configuration(configuration, logger.print_output)
    return configuration



## retrieve_sizes
# @author SAFFRAY Paul
# @version 1
# @brief Retrieve the additional sizes with more specific commands
def retrieve_sizes(path, kernel_version):
    """Retrieve additional sizes

    :param path: path to the compiled Linux kernel
    :type path: str
    :param kernel_version: version of the compiled Linux kernel to\
    retrieve the size from
    :type kernel_version: str
    :return: info about the retrieved sizes
    :rtype: dict
    """
    sizes_result = {}
    sizes_result['size_vmlinux'] = subprocess.run(['size {}/vmlinux'.format(path)], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    sizes_result['nm_size_vmlinux'] = bz2.compress(
                                    subprocess.run(["nm --size -r {}/vmlinux | sed 's/^[0]*//'".format(path)], shell=True, stdout=subprocess.PIPE).stdout)

    kversion = kernel_version.split(".") # eg 4.16 will give [4, 16]
    major = int(kversion[0]) # 4
    if len(kversion) >= 2:        
        minor = int(kversion[1]) # 16
    else:
        minor = 0
    if (major == 4 and minor >= 17) or major == 5: # see https://github.com/TuxML/ProjetIrma/issues/180 and https://gitlab.javinator9889.com/Javinator9889/thdkernel/commit/f49821ee32b76b1a356fab17316eb62430182ecf 
        sizes_result['size_builtin'] = bz2.compress(subprocess.run(['size {}/*/built-in.a'.format(path)], shell=True, stdout=subprocess.PIPE).stdout)
    else:
        sizes_result['size_builtin'] = bz2.compress(subprocess.run(['size {}/*/built-in.o'.format(path)], shell=True, stdout=subprocess.PIPE).stdout)
    return sizes_result


## run
# @author Picard Michaël
# @version 1
# @brief Do all the test, from compilation to sending the result to the database
# @details It does all the job, but for one and only one compilation. Therefore,
# it should be called multiple time for multiple compilation.
def run(boot, check_size, logger, configuration, environment,
        package_manager, tiny=False, config_file=None,
        cid_before=None, json=False):
    """Do all the tests, from compilation to sending the results to the
    database.

    It does all the job, but for one and only one
    compilation. Therefore, it should be called multiple time for
    multiple compilation.

    :param boot: boot the compiled kernel
    :type boot: bool
    :param check_size: check the size of the compiled kernel
    :type check_size: bool
    :param logger: logger
    :type logger: `Logger`_
    :param configuration: configuration info (See\
    :py:func:`retrieve_and_display_configuration`)
    :type configuration: dict
    :param environment: environment info (See\
    :py:func:`retrieve_and_display_environment`)
    :type environment: dict
    :param package_manager: package manager
    :type package_manager: `PackageManager <package_manager.html>`_
    :param tiny: use a tiny configuration or not
    :type tiny: bool
    :param config_file: path to a configuration file
    :type config_file: str
    :param cid_before:
    :type cid_before:

    """
    compiler = Compiler(
        logger=logger,
        package_manager=package_manager,
        nb_core=configuration['core_used'],
        kernel_path=configuration['kernel_path'],
        kernel_version=configuration['kernel_version_compilation'],
        tiny=tiny,
        config_file=config_file,
    )
    compiler.run()
    compilation_result = compiler.get_compilation_dictionary()

    boot_result = None
    size_result = None
    if compiler.is_successful():
        if check_size:
            size_result = retrieve_sizes(configuration['kernel_path'], configuration['kernel_version_compilation'])
        if boot:
            boot_checker = BootChecker(logger, configuration['kernel_path'])
            boot_checker.run()
            boot_result = boot_checker.get_boot_dictionary()
        else:
            logger.reset_boot_pipe()

    cid = 0
    try :
        cid = insert_result_into_database(
            logger,
            compilation_result,
            environment['hardware'],
            environment['software'],
            size_result,
            cid_before,
            boot_result,
        )
        archive_log(cid)

    except : 
        if cid == 0 :
            print("error sending log to database")
    else :
        if cid != 0 :
            cid = cid

    if json :
        json_file_creation(
                    cid = cid,
                    compilation_result1 = compilation_result['compilation_date'],
                    compilation_result2 = compilation_result['compilation_time'],
                    compilation_result3 = compilation_result['compiled_kernel_size'],
                    compilation_result4 = compilation_result['compiled_kernel_version'],
                    compilation_result5 = compilation_result['dependencies'],

                    compilation_result6 = compilation_result['number_cpu_core_used'],
                    compilation_result7 = compilation_result['compressed_compiled_kernel_size'],

                    compilation_result8 = open(compilation_result['stdout_log_file_path'], "r").read(),
                    compilation_result9 = open(compilation_result['stderr_log_file_path'], "r").read(),
                    compilation_result10 = open(compilation_result['user_output_file_path'], "r").read(),
                    gcc_version = environment["software"]["gcc_version"],
                    tiny=tiny,
                    config_file=config_file,
                    boot=boot,
                )    

    return cid


def json_file_creation(cid, compilation_result1, compilation_result2, compilation_result3, compilation_result4, compilation_result5,
compilation_result6, compilation_result7, compilation_result8, compilation_result9, compilation_result10, gcc_version, tiny, config_file, boot) :

    myJsonStruct = {
         'cid' : cid,
         'compilation_date' : compilation_result1,
         'compilation_time' : compilation_result2,
         'compiled_kernel_size' : compilation_result3,
         'compiled_kernel_version' : compilation_result4,
         'dependencies' : compilation_result5,
         'number_cpu_core_used' : compilation_result6,
         'compressed_compiled_kernel_size' : compilation_result7,
         'stdout_log_file' : compilation_result8,
         'stderr_log_file' : compilation_result9,
         'user_output_file' : compilation_result10,
         'gcc_version' : gcc_version,
         'tiny' : tiny,
         'config_file' : config_file,
         'boot' : boot,
        
    }

    with open('Json.json', 'w') as json_file:
        myJson = json.dump(myJsonStruct, json_file)


    
    
## archive_log
# @author PICARD Michaël
# @version 1
# @brief Retrieve the logs file, create a directory named <cid>, and put the log
# in the created directory.
def archive_log(cid):
    directory = "{}/{}".format(settings.LOG_DIRECTORY, cid)
    os.makedirs(directory)
    file_list = [file for file in os.listdir(settings.LOG_DIRECTORY)
                 if os.path.isfile(os.path.join(settings.LOG_DIRECTORY, file))]
    for file in file_list:
        shutil.copy2(
            os.path.join(settings.LOG_DIRECTORY, file),
            os.path.join(directory, file))


## insert_result_into_database
# @author PICARD Michaël
# @version 1
# @brief Send the sample result onto the data.
def insert_result_into_database(logger, compilation, hardware, software,
                                sizes=None, cid_incremental=None, boot=None):
    logger.timed_print_output("Sending result to database.")
    connection = fetch_connection_to_database(
        settings.IP_BDD,
        settings.USERNAME_BDD,
        settings.PASSWORD_USERNAME_BDD,
        settings.NAME_BDD)
    cursor = connection.cursor()

    hid = insert_if_not_exist_and_fetch_hardware(connection, cursor, hardware)
    sid = insert_if_not_exist_and_fetch_software(connection, cursor, software)
    compilation['hid'] = hid
    compilation['sid'] = sid
    cid = insert_and_fetch_compilation(connection, cursor, compilation)
    if cid_incremental is not None:
        insert_incrementals_compilation(
            connection, cursor,
            {'cid': cid, 'cid_base': cid_incremental, 'incremental_level': 1})
    if boot is not None:
        boot['cid'] = cid
        insert_boot_result(connection, cursor, boot)
    if sizes is not None:
        sizes['cid'] = cid
        insert_sizes(connection, cursor, sizes)

    logger.timed_print_output("Successfully sent results with cid : {}".format(
        cid), color=COLOR_SUCCESS)
    return cid


## remove_logs_file
# @author PICARD Michaël
# @version 1
# @brief Remove logs files, but not the logs that are "archived" ie put in a
# subdirectory.
def remove_logs_file():
    file_list = [file for file in os.listdir(settings.LOG_DIRECTORY)
                 if os.path.isfile(os.path.join(settings.LOG_DIRECTORY, file))]
    for file in file_list:
        os.remove(os.path.join(settings.LOG_DIRECTORY, file))


if __name__ == "__main__":
    # Initialisation
    args = parser()
    logger = create_logger(args.silent)
    package_manager = PackageManager(logger, settings.DEPENDENCIES_FILE)
    package_manager.update_system()
    environment = retrieve_and_display_environment(logger)
    configuration = retrieve_and_display_configuration(logger, args)

    # Do a compilation, do the test and send result
    run(
        args.boot,
        args.check_size,
        logger=logger,
        configuration=configuration,
        environment=environment,
        package_manager=package_manager,
        tiny=args.tiny,
        config_file=args.config,
        json=args.json
    )

    # Cleaning the container
    del logger
    remove_logs_file()
