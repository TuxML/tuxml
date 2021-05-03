#! /bin/bash 

# two arguments

# first is the path of the Linux kernel source
path=$1 
# "built-in.a" or "built-in.o"
builtin=$2

echo $path

total=0
echo "sym subsys"
for d in $(ls $path/*/$builtin)
do
    nb=$(grep .o $d | wc -l)
    total=$((total + nb))
    printf "%04d %s\n" $nb $d
done

arch=$(ls $path/arch/*/$builtin)
nb=$(grep .o $arch | wc -l)
total=$((total + nb))
printf "%04d %s\n" $nb $arch
printf "==========\n"
printf "%04d total\n" $total
printf "==========\n"
wc -l "$path/vmlinux.symvers"
wc -l "$path/vmlinux"





