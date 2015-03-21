#include "generated.c"
#include <stdio.h>
#include <sys/mman.h>

#ifndef threads
#define threads omp_get_max_threads()
#endif

int main (int argc, const char* argv[])
{
	size_t size = sizeof(float) * 1024*1024*1024;
	float* in = (float*) malloc(size);
	float* out = (float*) malloc(size);
	float* tmp;
	mlock(in, size);
	mlock(out, size);
	#pragma omp parallel for
	for (uint64_t i = 0; i < 1024; i++)
	{
		uint64_t ind[] = {0, 0, i};
		in[encode(ind)] = 1;
	}

	double t = omp_get_wtime();
	for (int i = 0; i < 5; i++)
	{
		apply(in, out);
	}
	double t2 = omp_get_wtime();
	munlock(in, size);
	munlock(out, size);
	for(uint64_t i = 0; i < 1024; i++)
	{
		uint64_t ind[] = {0, 0, i};
		printf("%f\t", out[encode(ind)]);
	}
	free(in);
	free(out);
	printf("Time: %f\n", t2-t);
	return 0;
}
