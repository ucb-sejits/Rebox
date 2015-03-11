#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include "zjacobi.c"


int main(int argc, const char* argv[])
{
	uint64_t iterations = 5;
	if (argc > 1)
	{
		iterations = atoi(argv[1]);
	}
	iterations  = 1 << iterations;
	int mod = 9;
	clock_t start;
	clock_t total = 0;
	srand(time(NULL));
	uint64_t x = (rand() % (1 << mod)) - (1 << (mod - 1));
	uint64_t y = (rand() % (1 << mod)) - (1 << (mod - 1));
	uint64_t z = (rand() % (1 << mod)) - (1 << (mod - 1));
	uint64_t z2 = rand() % (1 << mod);
	uint64_t i1[] = {x, y, z};
	uint64_t i2[] = {x, y, z2};
	uint64_t c1 = encode(i1);
	uint64_t c2 = encode(i2);
	uint64_t c3;
	uint64_t t = 0;
	start = clock();
	for (uint64_t i = 0; i < iterations; i++)
	{
//		t += encode(i1);
//		uint64_t k = x + y + z;
//		x = (x > 512 ? 512 : (x < 0 ? 0 : x));
//		y = (y > 512 ? 512 : (y < 0 ? 0 : y));
//		z = (z > 512 ? 512 : (z < 0 ? 0 : z));
//		clamp(&c1);
		c3 = add(c1, c2);
		clamp(&c3);
//		x *= 31;
//		y *= 31;
//		z *= 29;

	}
	printf("%d\r", t);
	printf("Total time: %f\n", ((float) clock()-start)/CLOCKS_PER_SEC);
}
