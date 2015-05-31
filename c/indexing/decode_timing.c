#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include "zdecode.c"
#include "zindex.c"

#ifndef SIZE
#define SIZE 1024
#endif

#pragma optimize( "", off )
int main() {
	uint64_t size = SIZE*SIZE*SIZE;
	printf("SIZE: %d\n", SIZE);
	clock_t start = clock();
	size_t result;
	size_t a, b, c;
	for (uint64_t x = 0; x < SIZE; x++) {
		for (uint64_t y = 0; y < SIZE; y++) {
			for (uint64_t z = 0; z < SIZE; z++) {
				result = encode(x, y, z);
				decode(result, &a, &b, &c);
				if (a != x || b != y || c != z) {
					printf("%d\t\t%d-%d\t%d-%d\t%d-%d\n", result, a, x, b, y, c, z);
				}
			}
		}
	}
	clock_t end = clock();
	for (uint64_t x = 0; x < SIZE; x++) {
		for (uint64_t y = 0; y < SIZE; y++) {
			for (uint64_t z = 0; z < SIZE; z++) {
				result = encode(x, y, z);
			}
		}
	}

	clock_t encode_time = clock() - end;
	clock_t diff = end - start;
	//printf("%d\r", result>>63);
	float elapsed = ((float) (diff - encode_time)) / CLOCKS_PER_SEC * 1000;
	printf("Elapsed Time: %f ms\n", elapsed);
}
