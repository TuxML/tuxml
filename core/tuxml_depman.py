#!/bin/python
import subprocess
import shutil
import tuxml_common as tcom


# author : LE FLEM Erwan
#
# [build_dependencies_arch description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_arch(missing_files, missing_packages):
    if tuxml_settings.DEBUG:
        tcom.pprint(3, "Arch based distro")

    cmd_check   = ""
    cmd_search  = "pkgfile -s {}" #pkgfile -s openssl/bio.h ne marche pas

    return 0


# author : LEBRETON Mickael
#
# [build_dependencies_debian description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_debian(missing_files, missing_packages):
    if tuxml_settings.DEBUG:
        tcom.pprint(3, "Debian based distro")

    cmd_search  = "apt-file search {}" # cherche dans quel paquet est le fichier
    cmd_check   = "dpkg-query -l | grep {}" # vérifie si le paquet est présent sur le système

    if tuxml_settings.DEBUG and len(missing_files) > 0:
        tcom.pprint(3, "Those files are missing :")

    for mf in missing_files:
        if tuxml_settings.DEBUG:
            print(" " * 3 + mf)

        output = subprocess.check_output([cmd_search.format(mf)], shell=True)

        # Sometimes the  output gives  several packages. The  program takes  the
        # first one and check if the package is already installed. If not, tuxml
        # installs it else it installs the next one
        lines = output.decode("utf-8").splitlines()
        i = 0
        status = 0
        while i < len(lines) and status == 0:
            package = lines[i].split(":")[0]
            # 0: package already installed
            # 1: package not installed
            status = subprocess.call([cmd_check.format(package)], stdout=tuxml_settings.OUTPUT, stderr=tuxml_settings.OUTPUT, shell=True)
            if status == 1:
                missing_packages.append(package)
            i += 1

        return missing_packages


# author :
#
# [build_dependencies_redhat description]
#
# return value :
#   -1 package not found
#    0 installation OK
def build_dependencies_redhat(missing_files, missing_packages):
    if tuxml_settings.DEBUG:
        tcom.pprint(3, "RedHat based distro")

    return 0


# authors : LE FLEM Erwan, MERZOUK Fahim
# Install packages of required dependencies to compile the kernel
# return zero on sucess, - 2 if no packages manager is found on error, other values for installation error.
def installDependency():
    pkg_manager = get_package_manager();
    if pkg_manager == None:
        return -2

    update_package_manager()
    #Installation of package with name common for all distributions.
    print("[*] Installation...")
    returnCode = installPackages(common_pkg)

    if (returnCode != 0):
        print("[-] Error while installing common packages")
        return returnCode

    # Now installation of packages with name that vary amongs distributions
    debian_specific = ["reiserfsprogs", "squashfs","quotatool", "nfs-kernel-server","procps", "mcelog", "libcrypto++6"
    ,"apt-utils"]

    arch_specific = ["reiserfsprogs", "squashfs-tools","quota-tools", "isdn4k-utils", "nfs-utils", "procps-ng", "oprofile"]

    redHat_specific =  ["reiserfs-utils", "squashfs-tools", "quotatool","isdn4k-utils", "nfs-utils", "procps-ng", "oprofile", "mcelog"]

    gentoo_specific =  ["reiserfsprogs", "squashfs-tools", "quotatool", "nfs-utils", "procps", "mcelog", "oprofile"]

    suse_specific =  ["reiserfs", "quota", "nfs-client", "procps"]

    packageSpecific = {"apt-get" : debian_specific, "pacman" : arch_specific, "dnf":redHat_specific, "yum":redHat_specific, "emerge":gentoo_specific, "zypper":suse_specific}
    returnCode = installPackages(packageSpecific[pkg_manager])

    if (returnCode != 0):
        print("[-] Error while installing distrib specific packages")
        return errorCode