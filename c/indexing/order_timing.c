#include <stdint.h>
#include <stdio.h>
#include <omp.h>
#ifdef Z
#include "zindex.c"
#else
#include "stdindex.c"
#endif

int main() {
	uint64_t dim_size = 1024;
	uint64_t size = dim_size*dim_size*dim_size;
	double start = omp_get_wtime();
	size_t result;
	for (int iter = 0; iter < 1; iter++) {
	for (uint64_t x = 0; x < dim_size; x++) {
		for (uint64_t y = 0; y < dim_size; y++) {
			for (uint64_t z = 0; z < dim_size; z++) {
				result = encode(x, y, z);
			}
		}
	}
	}
	double end = omp_get_wtime();
	printf("%d\r", result>>63);
#ifdef Z
	printf("Z\n");
#else
	printf("STD\n");
#endif
	printf("Elapsed Time: %f ms\n", (end - start) * 1000);
}
