#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include "zdecode.c"
#include "zindex.c"

#define MAX 256
#define ITERATIONS 1

#define millis_elapsed(a, b) (((double) (a - b) * 1000) / (CLOCKS_PER_SEC))

#pragma optimize( "", off )
int main() {
	size_t size = MAX*MAX*MAX;
	clock_t t0 = clock();
	size_t result;
	size_t a, b, c;
	for (uint64_t iter = 0; iter < ITERATIONS; iter++)
	{
		for (uint64_t x = 0; x < MAX; x++) {
			for (uint64_t y = 0; y < MAX; y++) {
				for (uint64_t z = 0; z < MAX; z++) {
					result = encode(x, y, z);
				}
			}
		}
	}
	clock_t t1 = clock();
	for (uint64_t iter = 0; iter < ITERATIONS; iter++)
	{
		for (uint64_t i = 0; i < size; i++) {
				decode(i, &a, &b, &c);
		}
	}
	clock_t t2 = clock();
	//printf("%d\r", result>>63);
	printf("Encode time %f ms, Decode time %f ms\n", millis_elapsed(t1, t0), millis_elapsed(t2, t1));
}
