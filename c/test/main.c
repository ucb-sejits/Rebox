#include "generated.c"
#include <stdio.h>

int main (int argc, const char* argv[])
{
	double* in = (double*) malloc(sizeof(double) * 1024*1024*1024);
	double* out = (double*) malloc(sizeof(double) * 1024 * 1024 * 1024);
	double t = omp_get_wtime();
	apply(in, out);
	double t2 = omp_get_wtime();
	free(in);
	free(out);
	printf("Time: %f\n", t2-t);
}
