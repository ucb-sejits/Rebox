@ /reserve/reserve.me
source activate ucb-sejits
touch z$1.log
for i in 6 7 8
do
python ../specializers/z_generator.py 3 $i > ../c/zjacobi.c
gcc -std=c99 -O3 -fopenmp -w zjacobi_main.c -o zjacobi_main_3_$i
echo $i >> z$1.log
./zjacobi_main $i $1 >> z$1.log
done
@ /reserve/unreserve.me