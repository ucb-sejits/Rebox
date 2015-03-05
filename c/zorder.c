#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include "zjacobi.c"


int main(int argc, const char* argv[])
{
	int mod = 6;
	clock_t start;
	clock_t total;
	srand(time(NULL));
	for (int i = 0; i < 1; i++)
	{
		uint64_t x = (rand() % (1 << mod)) - (1 << (mod - 1));
		uint64_t y = (rand() % (1 << mod)) - (1 << (mod - 1));
		uint64_t z = (rand() % (1 << mod)) - (1 << (mod - 1));
		uint64_t z2 = rand() % (1 << mod);
		uint64_t i1[] = {x, y, z};
		uint64_t i2[] = {x, y, z2};
		uint64_t i3[] = {2*x, 2*y, z+z2};
//		uint64_t i1[] = {1, 2, 3};
//		uint64_t i2[] = {-4, 5, -6};
//		uint64_t i3[] = {-3, 7, -3};
		start = clock();
		uint64_t c1 = encode(i1);
		uint64_t c2 = encode(i2);
		clamp(&c1);
		clamp(&c2);
		uint64_t c3 = add(c1, c2);
		uint64_t proper = encode(i3);
		clamp(&proper);
		clamp(&c3);

		total += clock() - start;
		if(c3 != proper)
		{
			printf("C1: %d\tC2: %d\n", c1, c2);
			printf("x: %d y:%d z:%d z2:%d\n", x, y, z, z2);
			printf("Expected: %d \tActual: %d\n", proper, c3);
		}
	}
	printf("Total time: %f\n", ((float) total)/CLOCKS_PER_SEC);
}
