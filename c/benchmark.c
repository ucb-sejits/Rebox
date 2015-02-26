/*
 * benchmark.c
 *
 *  Created on: Feb 24, 2011
 *      Author: nzhang-dev
 */

#include "zorder.c"

#include <time.h>

#include <time.h>
#include <stdlib.h>

#define SIZE (1<<16)

#define max (1 << BITS)

#define sClamp(x) (x < 0 ? 0 : (x > max ? max : x))

void stdClamp(uint32_t* code)
{
	uint32_t c = *code;
	uint32_t z = c & ((1 << (BITS + 1)) - 1);
	c >>= (BITS + 1);
	uint32_t y = c & ((1 << (BITS + 1)) - 1);
	c >>= (BITS + 1);
	uint32_t x = c & ((1 << (BITS + 1)) - 1);
	c >>= (BITS + 1);
	uint32_t w = c & ((1 << (BITS + 1)) - 1);
	w = sClamp(w);
	x = sClamp(x);
	y = sClamp(y);
	z = sClamp(z);
	*code = w << ((BITS + 1)*4) + x << ((BITS + 1)*3) + y << ((BITS + 1)*2) + z;

}

void stdAdd(uint32_t* code, uint32_t code2)
{
	*code += code2;
}


int main(int argc, char* argv[])
{
	srand(time(NULL));
	uint32_t stdRes[SIZE];
	uint32_t zRes[SIZE];
	for (int i = 0; i < SIZE; i++)
	{
		int w = rand() % (1 << (BITS + 1));
		int x = rand() % (1 << (BITS + 1));
		int y = rand() % (1 << (BITS + 1));
		int z = rand() % (1 << (BITS + 1));
		stdRes[i] = w;
		stdRes[i] <<= (BITS + 1);
		stdRes[i] |= x;
		stdRes[i] <<= (BITS + 1);
		stdRes[i] |= y;
		stdRes[i] <<= (BITS + 1);
		stdRes[i] |= z;
		zRes[i] = encode(encode(w, y), encode(x, z));
	}

	float stdtime = 0;
	float ztime = 0;

	for (int k = 0; k < 500; k++)
	{
		clock_t start = clock();
		for (int i = 0; i < SIZE; i++)
		{
			stdClamp(&stdRes[i]); //because otherwise if you have an overflow you corrupt the entire thing
			stdAdd(&stdRes[i], stdRes[i]);
			stdClamp(&stdRes[i]);

		}
		clock_t mid = clock();
		for (int i = 0; i < SIZE; i++)
		{
			add(&zRes[i], zRes[i]);
			clamp(&zRes[i]);
		}
		clock_t end = clock();
		stdtime += mid - start;
		ztime += end - mid;
	}
	printf("stdTime: %f\tzTime: %f\n", stdtime/CLOCKS_PER_SEC, ztime/CLOCKS_PER_SEC);
	return 0;
}
