#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "tmp.c"


int main(int argc, const char* argv[])
{
	uint32_t w = 3;
	uint32_t x = 5;
	uint32_t y = 7;
	uint32_t z = 21;
	uint32_t z2 = 14;
	uint32_t i1[] = {w, x, y, z};
	uint32_t i2[] = {w, x, y, z2};
	uint32_t i3[] = {2*w, 2*x, 2*y, z+z2};
	uint32_t c1 = encode(i1);
	uint32_t c2 = encode(i2);
	uint32_t c3 = add(c1, c2);
	clamp(&c3);
	printf("c1: %u\tc2: %u\n", c1, c2);
	printf("Sum: %d\n", c3);
	printf("Proper: %d\n", encode(i3));
}
