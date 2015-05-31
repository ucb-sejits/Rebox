#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include "zdecode.c"
#include "zindex.c"

int main() {
	uint64_t dim_size = 256;
	uint64_t size = dim_size*dim_size*dim_size;
	clock_t start = clock();
	size_t result;
	size_t a, b, c;
	for (uint64_t x = 0; x < dim_size; x++) {
			for (uint64_t y = 0; y < dim_size; y++) {
				for (uint64_t z = 0; z < dim_size; z++) {
					result = encode(x, y, z);
					decode(result, &a, &b, &c);
					if (a != x || b != y || c != z) {
						printf("%d-%d\t%d-%d\t%d-%d\n", a, x, b, y, c, z);
					}
				}
			}
		}
	clock_t end = clock();
	//printf("%d\r", result>>63);
	printf("Elapsed Time: %f ms\n", ((float) (end - start)) / CLOCKS_PER_SEC * 1000);
}
