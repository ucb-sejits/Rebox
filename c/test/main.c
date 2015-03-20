#include "generated.c"
#include <stdio.h>

int main (int argc, const char* argv[])
{
	float* in = (float*) malloc(sizeof(float) * 1024*1024*1024);
	float* out = (float*) malloc(sizeof(float) * 1024 * 1024 * 1024);
	double t = omp_get_wtime();
	for (int i = 0; i < 5; i++)
	{
		apply(in, out);
	}
	double t2 = omp_get_wtime();
	free(in);
	free(out);
	printf("Time: %f\n", t2-t);
	return 0;
}
