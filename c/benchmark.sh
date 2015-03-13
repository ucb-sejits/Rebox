source activate ucb-sejits
touch $2$1.log
for i in 6 7 8
do
python ../specializers/z_generator.py 3 $i > ../c/zjacobi.c
gcc -std=c99 -O3 -fopenmp -w $2.c -o $2
echo $i >> benchmarks/$2$1.log
./zjacobi_main $i $1 >> benchmarks/$2$1.log
done