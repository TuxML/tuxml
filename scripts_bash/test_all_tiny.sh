#!/bin/bash


# we assume that the script is executed at the root of tuxml... something like:
# bash scripts_bash/test_all_tiny.sh 

tableau_version_kernel=('5.8' '5.10' '5.15') # ('4.13.3' '4.15' '4.16' '4.17' '4.18' '4.20' '5.0' '5.1' '5.4' '5.7' '5.8')
# tableau_version_gcc=('clang9' 'gcc6' 'gcc8' 'clang11' 'gcc10')
tableau_version_gcc=('gcc8')

tagbuild='test-tiny-64bits'

for i in ${tableau_version_kernel[*]}
do
    for j in ${tableau_version_gcc[*]}
    do 
        python3 kernel_generator.py --dev --local --tiny --linux_version $i --compiler $j --json "build-$i-$j-$tagbuild.json" --mount_host_dev --preset compilation/x64.config --tagbuild "$tagbuild" --checksize
        echo 'build done for kernel version' $i 'with compiler' $j
    done 
done
