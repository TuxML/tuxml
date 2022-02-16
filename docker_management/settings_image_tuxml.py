LINUX_KERNEL = 'linux-4.13.3'

## Information about the base image
NAME_BASE_IMAGE = "tuxml/basetuxml-gcc6"

BASIC_DEP = "gcc g++ make binutils util-linux kmod readline-common e2fsprogs jfsutils xfsprogs btrfs-progs pcmciautils ppp grub iptables openssl bc reiserfsprogs squashfs-tools quotatool nfs-kernel-server procps libssl-dev wget qemu-system qemu-utils initramfs-tools lzop liblz4-tool dialog moreutils bison libelf-dev flex libdb5.3-dev qemu python3-distro"

CLANG_DEP = "clang clang-9"

COMPILER_GCC_DEV_6 = "gcc-6-plugin-dev"
COMPILER_GCC_DEV_8 = "gcc-8-plugin-dev"
COMPILER_GCC_DEV_10 = "gcc-10-plugin-dev"

# What will be written in the Dockerfile for the base image to produce the image.
CONTENT_BASE_IMAGE = {
    # Constants for the Dockerfile of the "compressed" image
    'DEBIAN_VERSION': 'FROM debian:stretch',
    'MKDIR_TUXML': "RUN mkdir /TuxML /TuxML/logs",
    'LINUX_TAR': "COPY linux-4.13.3.tar.xz /TuxML/linux-4.13.3.tar.xz\n"
                 "RUN echo \"4.13.3\" > /kernel_version.txt",
    'ENV_VARS': "ENV TZ=Europe/Paris\n"
                "ENV DEBIAN_FRONTEND noninteractive",
    'ZONEINFO': "RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone",
    'RUN_DEP': "RUN apt-get -qq -y update && apt-get -qq -y install python3 python3-dev python3-pip python3-setuptools default-libmysqlclient-dev apt-file apt-utils && apt-get install -qq -y --no-install-recommends --download-only " +
            BASIC_DEP + " " + COMPILER_GCC_DEV_6,
    'RUN_DEP_FILE': "RUN echo " + BASIC_DEP + " " + COMPILER_GCC_DEV_6 + " > /dependencies.txt",
    'RUN_PIP': "RUN pip3 install wheel mysqlclient psutil pytest pytest-cov requests",
    'CPRUN_BB': "COPY installBusyBox.sh /installBusyBox.sh\n"
                "COPY init /init\n"
                "RUN ./installBusyBox.sh\n"
                "RUN rm /installBusyBox.sh",
    'ADD_DEP': "COPY dependencies_tree_fixer.py /dependencies_tree_fixer.py\n"
               "RUN ./dependencies_tree_fixer.py\n"
               "RUN rm /dependencies_tree_fixer.py",
    'DEV' : "RUN cat /etc/issue"
}

## Information about the built image
NAME_IMAGE = "tuxml/tartuxml-gcc6"

# What will be written in the Dockerfile for the compressed docker image.
CONTENT_IMAGE = {
    # Constants for the Dockerfile of the "uncompressed" image
    'PREVIMG_VERSION': "FROM " + NAME_BASE_IMAGE,
    'TUXML_TAR': "COPY TuxML.tar.xz /TuxML/TuxML.tar.xz",
    'RUN_DEP': "",
    'RUN_DEP_FILE': "",
    'ENV_PYTHON': 'ENV PYTHONPATH=/TuxML',
    'DEV' : "RUN cat /etc/issue"
}


NAME_BIG_IMAGE = "tuxml/tuxml-gcc6"
CONTENT_BIG_IMAGE = {
    'PREVIMG_VERSION': "FROM " + NAME_IMAGE,
    'LINUX_UNTAR': "RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz",
    'TUXML_UNTAR': "RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz",
    'RUN_DEP_FILE': "RUN apt-get update && apt-get install -y --no-install-recommends $(cat /dependencies.txt)",
    'DEV' : "RUN cat /etc/issue"
}

##############################################
# 2
##############################################


## Information about the base image
NAME_BASE_IMAGE_2 = "tuxml/basetuxml-gcc8"

# What will be written in the Dockerfile for the base image to produce the image.
CONTENT_BASE_IMAGE_2 = {
    # Constants for the Dockerfile of the "compressed" image
    'DEBIAN_VERSION': 'FROM debian:buster',
    'MKDIR_TUXML': "RUN mkdir /TuxML /TuxML/logs",
    'LINUX_TAR': "COPY linux-4.13.3.tar.xz /TuxML/linux-4.13.3.tar.xz\n"
                 "RUN echo \"4.13.3\" > /kernel_version.txt",
    'ENV_VARS': "ENV TZ=Europe/Paris\n"
                "ENV DEBIAN_FRONTEND noninteractive",
    'ZONEINFO': "RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone",
    'RUN_DEP': "RUN apt-get -qq -y update && apt-get -qq -y install python3 python3-dev python3-pip python3-setuptools default-libmysqlclient-dev apt-file apt-utils && apt-get install -qq -y --no-install-recommends --download-only " +
            BASIC_DEP + " " + COMPILER_GCC_DEV_8,
    'RUN_DEP_FILE': "RUN echo " + BASIC_DEP + " " + COMPILER_GCC_DEV_8 + " > /dependencies.txt",
    'RUN_PIP': "RUN pip3 install wheel mysqlclient psutil pytest pytest-cov requests",
    'CPRUN_BB': "COPY installBusyBox.sh /installBusyBox.sh\n"
                "COPY init /init\n"
                "RUN ./installBusyBox.sh\n"
                "RUN rm /installBusyBox.sh",
    'ADD_DEP': "COPY dependencies_tree_fixer.py /dependencies_tree_fixer.py\n"
               "RUN ./dependencies_tree_fixer.py\n"
               "RUN rm /dependencies_tree_fixer.py",
    'DEV' : "RUN cat /etc/issue"
}

## Information about the built image
NAME_IMAGE_2 = "tuxml/tartuxml-gcc8"

# What will be written in the Dockerfile for the compressed docker image.
CONTENT_IMAGE_2 = {
    # Constants for the Dockerfile of the "uncompressed" image
    'PREVIMG_VERSION': "FROM " + NAME_BASE_IMAGE_2,
    'TUXML_TAR': "COPY TuxML.tar.xz /TuxML/TuxML.tar.xz",
    'RUN_DEP': "",
    'RUN_DEP_FILE': "",
    'ENV_PYTHON': 'ENV PYTHONPATH=/TuxML',
    'DEV' : "RUN cat /etc/issue"
}


NAME_BIG_IMAGE_2 = "tuxml/tuxml-gcc8"
CONTENT_BIG_IMAGE_2 = {
    'PREVIMG_VERSION': "FROM " + NAME_IMAGE_2,
    'LINUX_UNTAR': "RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz",
    'TUXML_UNTAR': "RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz",
    'RUN_DEP_FILE': "RUN apt-get update && apt-get install -y --no-install-recommends $(cat /dependencies.txt)",
    'DEV' : "RUN cat /etc/issue"
}


##############################################
# 3
##############################################


## Information about the base image
NAME_BASE_IMAGE_3 = "tuxml/basetuxml-gcc10"

# What will be written in the Dockerfile for the base image to produce the image.
CONTENT_BASE_IMAGE_3 = {
    # Constants for the Dockerfile of the "compressed" image
    'DEBIAN_VERSION': 'FROM debian:bullseye',
    'MKDIR_TUXML': "RUN mkdir /TuxML /TuxML/logs",
    'LINUX_TAR': "COPY linux-4.13.3.tar.xz /TuxML/linux-4.13.3.tar.xz\n"
                 "RUN echo \"4.13.3\" > /kernel_version.txt",
    'ENV_VARS': "ENV TZ=Europe/Paris\n"
                "ENV DEBIAN_FRONTEND noninteractive",
    'ZONEINFO': "RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone",
    'RUN_DEP': "RUN apt-get -qq -y update && apt-get -qq -y install python3 python3-dev python3-pip python3-setuptools default-libmysqlclient-dev apt-file apt-utils && apt-get install -qq -y --no-install-recommends --download-only " +
            BASIC_DEP + " " + COMPILER_GCC_DEV_10 + " " + CLANG_DEP ,
    'RUN_DEP_FILE': "RUN echo " + BASIC_DEP + " " + COMPILER_GCC_DEV_10 + " " + CLANG_DEP + " > /dependencies.txt",
    'RUN_PIP': "RUN pip3 install wheel mysqlclient psutil pytest pytest-cov requests",
    'CPRUN_BB': "COPY installBusyBox.sh /installBusyBox.sh\n"
                "COPY init /init\n"
                "RUN ./installBusyBox.sh\n"
                "RUN rm /installBusyBox.sh",
    'ADD_DEP': "COPY dependencies_tree_fixer.py /dependencies_tree_fixer.py\n"
               "RUN ./dependencies_tree_fixer.py\n"
               "RUN rm /dependencies_tree_fixer.py",
    'DEV' : "RUN cat /etc/issue"
}

## Information about the built image
NAME_IMAGE_3 = "tuxml/tartuxml-gcc10"

# What will be written in the Dockerfile for the compressed docker image.
CONTENT_IMAGE_3 = {
    # Constants for the Dockerfile of the "uncompressed" image
    'PREVIMG_VERSION': "FROM " + NAME_BASE_IMAGE_3,
    'TUXML_TAR': "COPY TuxML.tar.xz /TuxML/TuxML.tar.xz",
    'RUN_DEP': "",
    'RUN_DEP_FILE': "",
    'ENV_PYTHON': 'ENV PYTHONPATH=/TuxML',
    'DEV' : "RUN cat /etc/issue"
}


NAME_BIG_IMAGE_3 = "tuxml/tuxml-gcc10"
CONTENT_BIG_IMAGE_3 = {
    'PREVIMG_VERSION': "FROM " + NAME_IMAGE_3,
    'LINUX_UNTAR': "RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz",
    'TUXML_UNTAR': "RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz",
    'RUN_DEP_FILE': "RUN apt-get update && apt-get install -y --no-install-recommends $(cat /dependencies.txt)",
    'DEV' : "RUN cat /etc/issue"
}
