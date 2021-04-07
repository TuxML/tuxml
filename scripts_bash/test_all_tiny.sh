#!/bin/bash

tableau_version_kernel=('4.13.3' '4.15' '4.16' '4.17' '4.18' '4.20' '5.0' '5.1' '5.4' '5.7' '5.8')
tableau_version_gcc=('gcc6' 'gcc8' 'gcc10')

for i in ${tableau_version_gcc[*]}
do

for j in ${tableau_version_kernel[*]}
do 
python3 kernel_generator.py --dev --local --tiny --linux_version $j --compiler $i --json --mount_host_dev
echo 'end for' $i 'with' $j
done 
done

