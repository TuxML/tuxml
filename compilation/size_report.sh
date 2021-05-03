#! /bin/bash 

path=$1 
echo $path

total=0
echo "sym subsys"
for d in $(ls $path/*/built-in.a)
do
    nb=$(grep .o $d | wc -l)
    total=$((total + nb))
    printf "%04d %s\n" $nb $d
done

arch=$(ls $path/arch/*/built-in.a)
nb=$(grep .o $arch | wc -l)
total=$((total + nb))
printf "%04d %s\n" $nb $arch
echo "----------"
printf "%04d total\n" $total
printf "\n==========\n"
wc -l "$path/vmlinux.symvers"
wc -l "$path/vmlinux"
