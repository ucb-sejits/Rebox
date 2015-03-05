/*
 * testClamp.c
 *
 *  Created on: Mar 4, 2015
 *      Author: nzhang-dev
 */


#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include "zjacobi.c"

#define sClamp(x) (x > (1 << mod) ? (1 << mod) : (x < 0 ? 0 : x))

int main(int argc, const char* argv[])
{
	int iterations = 24;
	int negative = 1;
	srand(time(NULL));
	int32_t mod = 3;
	clock_t start = clock();
	clock_t total = 0;
	for(int i = 0; i < (1 << iterations); i++)
	{
		int64_t x = (rand() % (1 << mod));
		int64_t y = (rand() % (1 << mod));
		int64_t z = (rand() % (1 << mod));

		if(negative == 1)
		{
			x -= (1 << (mod - 1));
			y -= (1 << (mod - 1));
			z -= (1 << (mod - 1));
		}
		int64_t code[] = {x, y, z};

		int64_t xc = sClamp(x);
		int64_t yc = sClamp(y);
		int64_t zc = sClamp(z);
		int64_t code2[] = {xc, yc, zc};
		start = clock();
		uint64_t encode1 = encode(code);
		clamp(&encode1);
		uint64_t encode2 = encode(code2);
		total += clock() - start;
		if (encode1 != encode2)
		{
			printf("%u\t%u\t%d\t%d\t%d\n", encode1, encode2, x, y, z);
		}
	}
	printf("Time elapsed: %f\n", ((float) total) / CLOCKS_PER_SEC);


}
