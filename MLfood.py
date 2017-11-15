#!/usr/bin/python3

import os
from sys import argv


# Error if there is no argument "number" of compilation to run.
if len(argv) == 1 :
    print("Please specify a number of compilation to launch.")
    print("Command ./MLfood.py [Integer]")
    exit()

# Convert the parameter in an Integer which is the number of compilation to do.
# If the number is above 50, the scrypt will ask for a confirmation
try:
    nb = int(argv[1])
    if nb > 50 :
        print("Are-you sure you want to start {} compilation? (y/n)".format(nb))
        ok = input();
        ok.lower()
        if ok != "y":
            print("Canceled")
            exit()

except Exception as e:
    print("Please specify a valide number of compilation to launch.")
    print("Command ./MLfood.py [Integer]")
    exit()

# Retrieves the number of compilation to run.

if nb <= 0:
    print("Please enter a non-zero positive integer.")
    exit()

# Must contain the list of differents systems images URLs with the execution tuxml script.
images = ["tuxml/tuxmldebian:latest"]

# The image list must not be empty.
if len(images) == 0:
	print("There is no images.")
	exit()

# For each url in the url list "images", we run a new docker which run the TuxML command.
for i in range(nb):
    str2 = "sudo docker pull {} ".format(images[i % len(images)])
    print("Recuperation dernière version de l'image {}".format(images[i % len(images)]))
    os.system(str2)
    print("\n=============== Docker n°{} ===============".format(i+1))
    chaine = 'sudo docker run -it {} /TuxML/tuxml.py /TuxML/linux-4.13.3 --debug'.format(images[i % len(images)])
    print(chaine)
    print("==========================================\n")
    os.system(chaine)
