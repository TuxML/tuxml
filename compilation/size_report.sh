#! /bin/bash 

# two arguments

# first is the path of the Linux kernel source
path=$1 
# "built-in.a" or "built-in.o"
builtin=$2

echo $path

echo "size in subsys"
for d in $(ls $path/*/$builtin)
do
    sz=$(size -t $d)
    printf "%s\n%s" "$d" "$sz"
    # echo -n "$d\n$sz"
    printf "\n==========\n"
done

arch=$(ls $path/arch/*/$builtin)
sz=$(size -t $arch)
printf "%s\n%s" "$arch" "$sz"
printf "\n==========\n"





