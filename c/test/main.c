#include "generated.c"
#include <stdio.h>
 #include <sys/mman.h>

void dump(float values[], uint32_t row_len, uint32_t rows)
{
	for(uint32_t j = 0; j < rows; j++)
	{
		for(uint32_t i = row_len*j; i < row_len*(j+1); i++)
		{
			printf("%f\t", values[i]);
		}
		printf("\n");
	}
	printf("\n");
}


int main (int argc, const char* argv[])
{
	size_t size = sizeof(float) * 1024*1024*1024;
	float* in = (float*) malloc(size);
	float* out = (float*) malloc(size);
	float* tmp;
	mlock(in, size);
	mlock(out, size);
//	for (uint64_t i = 0; i < 1024; i++)
//	{
//		uint64_t ind[] = {0, 0, i};
//		in[encode(ind)] = 1;
//	}
//	for (int i = 0; i < 1024; i++)
//	{
//			uint64_t ind[] = {0, 0, i};
			//printf("%f\t", in[encode(ind)]);
//	}
	double t = omp_get_wtime();
	for (int i = 0; i < 5; i++)
	{
		apply(in, out);
	}
	double t2 = omp_get_wtime();
//	for(uint64_t i = 0; i < 1024; i++)
//	{
//		uint64_t ind[] = {0, 0, i};
//		printf("%f\t", out[encode(ind)]);
//	}
	printf("\n");
	munlock(in, size);
	munlock(out, size);
	free(in);
	free(out);
	printf("Time: %f\n", t2-t);
	return 0;
}
