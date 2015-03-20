#include "generated.c"
#include <stdio.h>
 #include <sys/mman.h>

int main (int argc, const char* argv[])
{
	size_t size = sizeof(float) * 1024*1024*1024;
	float* in = (float*) malloc(size);
	float* out = (float*) malloc(size);
	mlock(in, size);
	mlock(out, size);
	double t = omp_get_wtime();
	for (int i = 0; i < 5; i++)
	{
		apply(in, out);
	}
	double t2 = omp_get_wtime();
	munlock(in, size);
	munlock(out, size);
	free(in);
	free(out);
	printf("Time: %f\n", t2-t);
	return 0;
}
