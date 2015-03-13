source activate ucb-sejits

rm benchmarks/$2$1.log
touch benchmarks/$2$1.log
for i in 6 7 8 9 10
do
python ../specializers/z_generator.py 3 $i > ../c/zjacobi.c
gcc -std=c99 -O3 -fopenmp -w $2.c -o $2
echo $i >> benchmarks/$2$1.log
./$2 $i $1 >> benchmarks/$2$1.log
done