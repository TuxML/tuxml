#!/usr/bin/python3

## @file build_image_tuxml.py
# @author DIDOT Gwendal ACHER Mathieu PICARD Michaël
# @copyright Apache License 2.0
# @brief Script use to simplified creation and uses of Docker images.
# @details This script id design to help members of the TuxML project to easily
# use Docker, without any knowledge require other than what a Docker image is
# (check https://docs.docker.com/get-started/ for more information).

import argparse
import subprocess
import os
import shutil

from settings_image_tuxml import *


## docker_build
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief build a docker image
# @param image The image name of your choice. Default to None.
# @param tag The tag of your choice. Default to None.
# @param path The path where the Dockerfile is. Default to None, which is
# equivalent to . (current directory).
def docker_build(image=None, tag=None, path=None):
    if path is None:
        path = "."
    str_build = "docker build".format(image)
    if image is not None:
        str_build = "{} -t {}".format(str_build, image)
        if tag is not None:
            str_build = "{}:{}".format(str_build, tag)
    str_build = "{} {}".format(str_build, path)
    subprocess.run(str_build, shell=True)


## docker_push
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief push a docker image
# @param image The name of the image to push.
# @param tag The tag of the image to push.
def docker_push(image, tag=None):
    str_push = "docker push {}".format(image)
    if tag is not None:
        str_push = "{}:{}".format(str_push, tag)
    result_push = subprocess.call(args=str_push, shell=True)
    if result_push == 1:
        print("You need to login on Docker hub\n")
        subprocess.run(args="docker login", shell=True)
        docker_push(image=image, tag=tag)


## docker_pull
# @author PICARD Michaël
# @version 1
# @brief pull a docker image
# @param image The image name that you want to pull.
# @param tag The tag's image. Default to None.
def docker_pull(image, tag=None):
    str_pull = "docker pull {}".format(image)
    if tag is not None:
        str_pull = "{}:{}".format(str_pull, tag)
    subprocess.call(args=str_pull, shell=True)


## create_dockerfile
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief Create and save a Dockerfile
# @param content What you will actually put in your Dockerfile. Default to None.
# @param path Where you want to save your Dockerfile. Default to None, which is
# # equivalent to . (current directory).
def create_dockerfile(content=None, path=None):
    if path is not None:
        os.chdir(path)
    with open("Dockerfile", "w") as file:
        file.write(content)


## create_sub_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Create a base image to speed our usual build
# @details It create an image on which we will build the image to upload. Its
# goal is to speed up the creation context when we just update project's files,
# and not the whole dependencies for our project.
def create_sub_image_tuxml_compressed(NameContent, tmp_location):
    get_linux_kernel(LINUX_KERNEL, tmp_location)
    # we need to ensure that the Dockerfile, installBusyBox.sh and init are in
    # the same directory
    # same for dependencies_tree_fixer.py
    MyNameContent = ""
    MyNameBaseImage = ""

    if NameContent == NAME_IMAGE:
        MyNameContent = CONTENT_BASE_IMAGE
        MyNameBaseImage = NAME_BASE_IMAGE
    elif NameContent == NAME_IMAGE_2:
        MyNameContent = CONTENT_BASE_IMAGE_2
        MyNameBaseImage = NAME_BASE_IMAGE_2
    elif NameContent == NAME_IMAGE_3 :
        MyNameContent = CONTENT_BASE_IMAGE_3
        MyNameBaseImage = NAME_BASE_IMAGE_3
    if os.path.abspath(tmp_location) != os.path.dirname(
            os.path.abspath(__file__)):
        shutil.copy2(
            "{}/installBusyBox.sh".format(
                os.path.dirname(os.path.abspath(__file__))),
            "{}/installBusyBox.sh".format(tmp_location))
        shutil.copy2(
            "{}/init".format(os.path.dirname(os.path.abspath(__file__))),
            "{}/init".format(tmp_location))
        shutil.copy2(
            "{}/dependencies_tree_fixer.py".format(os.path.dirname(os.path.abspath(__file__))),
            "{}/dependencies_tree_fixer.py".format(tmp_location))

    content = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        MyNameContent['DEBIAN_VERSION'],
        MyNameContent['MKDIR_TUXML'],
        MyNameContent['LINUX_TAR'],
        MyNameContent['ENV_VARS'],
        MyNameContent['ZONEINFO'],
        MyNameContent['RUN_DEP'],
        MyNameContent['RUN_DEP_FILE'],
        MyNameContent['RUN_PIP'],
        MyNameContent['CPRUN_BB'],
        MyNameContent['ADD_DEP'],
        MyNameContent['DEV']
    )
    create_dockerfile(
        content=content,
        path=tmp_location)
    docker_build(
        image=MyNameBaseImage,
        path=tmp_location)

    if os.path.abspath(tmp_location) != os.path.dirname(os.path.abspath(__file__)):
        os.remove("{}/installBusyBox.sh".format(tmp_location))
        os.remove("{}/init".format(tmp_location))
        os.remove("{}/dependencies_tree_fixer.py".format(tmp_location))
#################################################
# 1
#################################################
## create_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Create the compressed image to work with.
# @param tmp_location Where we create and build the image.
# @param tag The tag of the built image. Default to None.
# @param dependencies_path The path to the file corresponding to optional
# dependencies. Default to None.
def create_image_tuxml_compressed(NameContent ,tmp_location, tag=None, dependencies_path=None):
    MyNameContent = ""
    MyNameImage = ""

    if NameContent == NAME_IMAGE:
        MyNameContent = CONTENT_IMAGE
        MyNameImage = NAME_IMAGE
    elif NameContent == NAME_IMAGE_2:
        MyNameContent = CONTENT_IMAGE_2
        MyNameImage = NAME_IMAGE_2
    elif NameContent == NAME_IMAGE_3:
        MyNameContent = CONTENT_IMAGE_3
        MyNameImage = NAME_IMAGE_3

    tmp_content = MyNameContent
    if dependencies_path is not None:
        with open(dependencies_path) as dep_file:
            str_dep = ''
            tmp = dep_file.readline()
            while tmp != '':
                str_dep += tmp + " "
                tmp = dep_file.readline()
            str_dep = str_dep.replace("\n", "")
        tmp_content['RUN_DEP'] =\
            "RUN apt-get install -qq -y --no-install-recommends --download-only {} ".format(str_dep)
        tmp_content['RUN_DEP_FILE'] = "RUN echo {} >> /dependencies.txt".format(str_dep)
    content = "{}\n{}\n{}\n{}\n{}\n{}".format(
        tmp_content['PREVIMG_VERSION'],
        tmp_content['TUXML_TAR'],
        tmp_content['RUN_DEP'],
        tmp_content['RUN_DEP_FILE'],
        tmp_content['ENV_PYTHON'],
        tmp_content['DEV']
    )
    create_dockerfile(
        content=content,
        path=tmp_location)
    docker_build(
        image= MyNameImage,
        tag=tag,
        path=tmp_location)
    os.remove("{}/TuxML.tar.xz".format(tmp_location))
#################################################
# 1
####################################################################################################################################
## create_big_image_tuxml_uncompressed
# @author PICARD Michaël
# @version 1
# @brief Create the uncompressed image to work with.
# @param tmp_location Where we create and build the image.
# @param tag The tag of the built image. Default to None.
# @param dependencies_path The path to the file corresponding to optional
# dependencies. Default to None.
def create_big_image_tuxml_uncompressed(NameContent, tmp_location, tag=None):
    MyNameContent = ""
    MyBigImage = ""

    if NameContent == NAME_IMAGE:
        MyNameContent = CONTENT_BIG_IMAGE
        MyBigImage = NAME_BIG_IMAGE
    elif NameContent == NAME_IMAGE_2:
        MyNameContent = CONTENT_BIG_IMAGE_2
        MyBigImage = NAME_BIG_IMAGE_2
    elif NameContent == NAME_IMAGE_3 :
        MyNameContent = CONTENT_BIG_IMAGE_3
        MyBigImage = NAME_BIG_IMAGE_3
    
    content = "{}".format(MyNameContent['PREVIMG_VERSION'])
    if tag is not None:
        content = "{}:{}".format(content, tag)
    content = "{}\n{}\n{}\n{}\n{}".format(
        content,
        MyNameContent['TUXML_UNTAR'],
        MyNameContent['LINUX_UNTAR'],
        MyNameContent['RUN_DEP_FILE'],
        MyNameContent['DEV']
    )
    create_dockerfile(content=content, path=tmp_location)
    docker_build(
        image=MyBigImage,
        tag=tag,
        path=tmp_location
    )
    os.remove("{}/Dockerfile".format(tmp_location))

#############################################################
#################################################
# 1
#####################################################################################
## exist_sub_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Test if the sub_image_tuxml_compressed docker image already exist.
# @return Boolean
def exist_sub_image_tuxml_compressed(NameofImage):
    cmd = "docker image ls --format {{.Repository}} | grep"
    cmd = "{} {}".format(cmd, NameofImage)
    # mpicard: grep return 0 if a line is found, 1 is no line found and 2 or
    # greater if an error occured. So we just check it.
    returncode = subprocess.call(
        args=cmd,
        shell=True,
        stdout=subprocess.DEVNULL
    )
    return returncode == 0
#####################################################################################
##get_linux_kernel
# @author POLES Malo, PICARD Michaël
# @version 2
# @brief Download the linux kernel at the current location
# @param name Specify version of kernel we want. MUST BE A v4.x version.
def get_linux_kernel(name, path=None):
    if path is not None:
        os.chdir(path)
    name += ".tar.xz"
    list_dir = os.listdir('.')
    if name not in list_dir:
        print("Linux kernel not found, downloading...")
        wget_cmd = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/{}".format(name)
        subprocess.run(args=wget_cmd, shell=True)
    else:
        print("Linux kernel found.")


## ask_for_confirmation
# @author POLES Malo, PICARD Michaël
# @version 2
# @brief Ask a confirmation, and return the answer as boolean
# @return Boolean
def ask_for_confirmation():
    answer = input().lower()
    while answer != 'n' and answer != 'y':
        print("y/n")
        answer = input().lower()
    return answer == 'y'


## create_tuxml_archive
# @author THOMAS Luis, PICARD Michaël
# @version 2
# @brief Pack all necessary file inside the archive TuxML.tar.xz
def create_tuxml_archive(path):
    cmd = "mkdir {}/TuxML".format(path)
    subprocess.call(args=cmd, shell=True)
    cmd = "cp -r {}/../compilation {}/TuxML".format(
        os.path.dirname(os.path.abspath(__file__)),
        path
    )
    subprocess.call(args=cmd, shell=True)
    cmd = "cp -r {}/../tests {}/TuxML".format(
        os.path.dirname(os.path.abspath(__file__)),
        path
    )
    subprocess.call(args=cmd, shell=True)

    os.chdir("{}/TuxML".format(path))
    subprocess.call(args="tar -cf TuxML.tar.xz *", shell=True)
    subprocess.call(args="mv TuxML.tar.xz ../TuxML.tar.xz", shell=True)
    os.chdir("..")
    subprocess.call(args="rm -rf TuxML", shell=True)


#################################################
# 1
################################################### 
# @author PICARD Michaël
# @version 1
# @brief Parse the commandline and result the parsed result.
def parser():
    parser = argparse.ArgumentParser(
        description=""  # TODO: Fill the description
    )
    parser.add_argument(
        '-p',
        '--push',
        help="Push the image on the distant repository",
        action="store_true"
    )
    parser.add_argument(
        '-t',
        '--tag',
        help="Tag of the image you want to generate/build/push/pull."
	     " Default to \"dev\"",
        default="dev"
    )
    parser.add_argument(
        '-d',
        '--dependencies',
        help="Dependencies you want to add to your docker image when you "
             "generate your dockerfile"
    )
    parser.add_argument(
        '-f',
        '--full_rebuild',
        help="Force the rebuild of the core system image, which is not needed "
             "in most of the case.",
        action="store_true"
    )
    parser.add_argument(
        "-l",
        "--location",
        help="Where you want to create your directory to generate/build. "
             "Default is current",
        default="."
    )
    parser.add_argument(
        "-u",
        "--update",
        help="Download the image from the repository",
        action="store_true"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parser()
    listeArg = [NAME_IMAGE, NAME_IMAGE_2, NAME_IMAGE_3]
    confirm_build = 0

    for i in listeArg:
        if args.push:
            docker_push(i, args.tag)
        elif args.update:
            docker_pull(i, args.tag)
            create_big_image_tuxml_uncompressed(i ,args.location, tag=args.tag)
        else:
            if not exist_sub_image_tuxml_compressed(i):
                create_sub_image_tuxml_compressed(i, args.location)
            elif args.full_rebuild:
                print("Are you sure that you want to rebuild the whole docker image"
                    " project (Y/n)? ")
                if confirm_build:
                    create_sub_image_tuxml_compressed(i, args.location)
                elif ask_for_confirmation():
                    confirm_build = 1
                    create_sub_image_tuxml_compressed(i, args.location)
                else:
                    print("Whole rebuild canceled.\n")
            create_tuxml_archive(args.location)
            # TODO: Removing of old image, in order to have a clean docker image registry
            # check kernel_generator.py:docker_image_auto_cleaner for more.
            create_image_tuxml_compressed(i ,args.location, args.tag, args.dependencies)
            create_big_image_tuxml_uncompressed(i ,args.location, tag=args.tag)
