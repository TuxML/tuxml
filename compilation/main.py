#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess
import bz2
import json

from compilation.apiManager import APIManager
from compilation.environment import get_environment_details, print_environment_details
from compilation.configuration import create_configuration, print_configuration
from compilation.package_manager import PackageManager
from compilation.logger import Logger, COLOR_SUCCESS, COLOR_ERROR
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
        "--clang_version",
        type=int,
        help="clang version to use. Only versions 9 and 11 are supported. "
             "May not work with all images (right now works only for Docker image with gcc10). 0 to use GCC, which is default.",
        default=0
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
        help="Serialize into a JSON file with informations about the build."
    )
    parser.add_argument(
        "--mount_host_dev",
        action="store_true",
        help="Should be used for development only. Enables to use local source code without regenerating Docker images."
    )

    parser.add_argument(
        "--tagbuild",
        type=str,
        nargs="*",
        default=None,
        help="Optional. Enables to tag a compilation or a set of compilations (with a string)"
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
def retrieve_and_display_environment(logger, clang_version=0):
    """Retrieve and display the environment details

    :param logger: the logger
    :type logger: `Logger`_
    :param clang_version: clang compiler version (if any)
    :type clang_version: int (0: gcc and no clang; 9 or 11 supported right now)
    :return: the environment
    :rtype: dict
    """
    logger.timed_print_output("Getting environment details.")
    environment = get_environment_details(clang_version)
  

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

    # too much (deprecated)
    # sizes_result['nm_size_vmlinux'] = bz2.compress(
    #                                subprocess.run(["nm --size -r {}/vmlinux | sed 's/^[0]*//'".format(path)], shell=True, stdout=subprocess.PIPE).stdout)

    kversion = kernel_version.split(".") # eg 4.16 will give [4, 16]
    major = int(kversion[0]) # 4
    if len(kversion) >= 2:        
        minor = int(kversion[1]) # 16
    else:
        minor = 0
    
    builtin=None
    if (major == 4 and minor >= 17) or major == 5: # see https://github.com/TuxML/ProjetIrma/issues/180 and https://gitlab.javinator9889.com/Javinator9889/thdkernel/commit/f49821ee32b76b1a356fab17316eb62430182ecf 
        builtin="built-in.a"       
    else:
        builtin="built-in.o"

    # size_report should be preferred (some might be deprecated in the future)
    # limitation: does not include totals per built-in (deprecated)
    # sizebuilt1 = subprocess.run(['size {}/*/{}'.format(path, builtin)], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8') 
    # sizebuilt2 = subprocess.run(['size {}/arch/*/{}'.format(path, builtin)], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8') 
    # sizes_result['size_builtin'] = sizebuilt1 + "\n" + sizebuilt2

    # two arguments for the bash scripts: path and kind of built-in (.a or .o)
    sizes_result['size_report_builtin'] = subprocess.run(['bash {} {} {}'.format(settings.SIZE_REPORT_FILE, path, builtin)], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8') # full report 
    sizes_result['size_report_builtin_coarse'] = subprocess.run(['bash {} {} {}'.format(settings.SIZE_REPORT_COARSE_FILE, path, builtin)], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8') # coarse grained report (rough summary)
    return sizes_result




## run
# @author Picard Michaël
# @version 1
# @brief Do all the test, from compilation to sending the result to the database
# @details It does all the job, but for one and only one compilation. Therefore,
# it should be called multiple time for multiple compilation.
def run(boot, check_size, logger, configuration, environment,
        package_manager, tiny=False, config_file=None,
        cid_before=None, json_bool=False, clang_version=0, tagbuild=None):
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
    :param clang_version: Clang version to use. 0 to use GCC. Only 9 and 11 are
        supported on Debian 11.
    :type clang_version: int
    :type tag: str

    """
    compiler_exec = 'gcc'
    if clang_version == 9:
        compiler_exec = 'clang-9'
    elif clang_version == 11:
        compiler_exec = 'clang'

    compiler = Compiler(
        logger=logger,
        package_manager=package_manager,
        nb_core=configuration['core_used'],
        kernel_path=configuration['kernel_path'],
        kernel_version=configuration['kernel_version_compilation'],
        tiny=tiny,
        config_file=config_file,
        compiler_exec=compiler_exec
    )
    compiler.run()
    compilation_result = compiler.get_compilation_dictionary()
    environmenthard = environment['hardware']
    environmentsoft = environment["software"]
  


    boot_result = None
    # by default size report is not performed
    sizes_result = {'size_vmlinux': -2, 'size_report_builtin': None, 'size_report_builtin_coarse': None}  
    if compiler.is_successful():
        if check_size:
            sizes_result = retrieve_sizes(configuration['kernel_path'], configuration['kernel_version_compilation']) 
        if boot:
            boot_checker = BootChecker(logger, configuration['kernel_path'])
            boot_checker.run()
            boot_result = boot_checker.get_boot_dictionary()
        else:
            logger.reset_boot_pipe()

    cid = 0
    tagbuild_str = ""
    if tagbuild:
        tagbuild_str = ' '.join(tagbuild)


    configfile = open("{}/.config".format(compiler.get_kernel_path()), "r").read()
    json_data = {'cid': 0, 'compilation_date': compilation_result['compilation_date'],
                 'compilation_time': compilation_result['compilation_time'],
                 'compiled_kernel_size': compilation_result['compiled_kernel_size'],
                 'compiled_kernel_version': compilation_result['compiled_kernel_version'],
                 'dependencies': compilation_result['dependencies'],
                 'number_cpu_core_used': compilation_result['number_cpu_core_used'],
                 'compressed_compiled_kernel_size': compilation_result['compressed_compiled_kernel_size'],
                 'stdout_log_file': open(logger.get_stdout_file(), "r").read(),
                 'stderr_log_file': open(logger.get_stderr_file(), "r").read(),
                 'user_output_file': open(logger.get_user_output_file(), "r").read(),
                 'compiler_version': environmentsoft["compiler_version"],
                 'tiny': tiny, 'config_file': configfile, 'boot': boot,
                 'cpu_brand_name': environmenthard['cpu_brand_name'],
                 'cpu_max_frequency': environmenthard['cpu_max_frequency'], 'ram_size': environmenthard['ram_size'],
                 'architecture': environmenthard['architecture'], 'number_cpu_core': environmenthard['number_cpu_core'],
                 'mechanical_disk': environmenthard['mechanical_disk'], 'libc_version': environmentsoft['libc_version'],
                 'tuxml_version': environmentsoft['tuxml_version'], 'system_kernel': environmentsoft['system_kernel'],
                 'linux_distribution': environmentsoft['linux_distribution'],
                 'linux_distribution_version': environmentsoft['linux_distribution_version'],
                 'system_kernel_version': environmentsoft['system_kernel_version'], 
                 'tagbuild': tagbuild_str, 
                 # TODO: same key, refactor code
                 'size_vmlinux': sizes_result['size_vmlinux'], 
                 'size_report_builtin': sizes_result['size_report_builtin'],
                 'size_report_builtin_coarse': sizes_result['size_report_builtin_coarse']
                 }
                 # 

    apiManager = APIManager()
    response = apiManager.sendPost(json_data)
    if (response.status_code == 201): 
        cid = response.json()
        logger.timed_print_output(
            "Compilation send to TuxML API.",
            color=COLOR_SUCCESS
        )
        logger.timed_print_output(
            "CID received from database : " + str(cid),
            color=COLOR_SUCCESS
        )

    else:
        logger.timed_print_output(
            "Error received from TuxML API when sending compilation.",
            color=COLOR_ERROR
        )
        logger.timed_print_output(
            "Status code : " + str(response.status_code),
            color=COLOR_ERROR
        )
        logger.timed_print_output(
            "Error message : " + response.text,
            color=COLOR_ERROR
        )
        
    if json_bool :
        create_json_file(cid, json_data)

    return cid

def create_json_file(cid, json_data):
    json_data["cid"] = cid

    with open(settings._JSON_INTERNAL_FILENAME, 'w') as json_file:
        json.dump(json_data, json_file)


    
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
    environment = retrieve_and_display_environment(logger, args.clang_version)
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
        json_bool=args.json,
        clang_version=args.clang_version,
        tagbuild=args.tagbuild
    )

    # Cleaning the container
    del logger
    remove_logs_file()
