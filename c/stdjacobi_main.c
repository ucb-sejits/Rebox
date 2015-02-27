/*
 * stdjacobi_main.c
 *
 *  Created on: Feb 26, 2015
 *      Author: nzhang-dev
 */
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>

#define NDIM 3

#include "kernel.c"


#define sClamp(x) (x < 0 ? 0 : (x >= array_size ? array_size - 1 : x))

int main(int argc, char* argv[])
{
	printf("Allocating problem\n");
	uint64_t array_size = 1 << 9;
	uint32_t iterations = 1;
	if (argc > 1)
	{
		array_size = atoi((const char*) argv[1]);
	}
	if (argc > 2)
	{
		iterations = atoi((const char*) argv[2]);
	}
	printf("Malloccing\n");
	uint32_t*** data = (uint32_t***) malloc(sizeof(uint32_t**) * array_size);
	for (int i = 0; i < array_size; i++)
	{
		uint32_t** sub = (uint32_t**) malloc(sizeof(uint32_t*) * array_size);
		data[i] = sub;
		for (int j = 0; j < array_size; j++)
		{
			uint32_t* subsub = (uint32_t*) malloc(sizeof(uint32_t*) * array_size);
			sub[j] = subsub;
		}
	}

	uint32_t*** out = (uint32_t***) malloc(sizeof(uint32_t**) * array_size);
	for (int i = 0; i < array_size; i++)
	{
		uint32_t** sub = (uint32_t**) malloc(sizeof(uint32_t*) * array_size);
		out[i] = sub;
		for (int j = 0; j < array_size; j++)
		{
			uint32_t* subsub = (uint32_t*) malloc(sizeof(uint32_t*) * array_size);
			sub[j] = subsub;
		}
	}

	for (int y = 0; y < array_size; y++)
	{
		for(int z = 0; z < array_size; z++)
		{
			data[0][y][z] = 300;
			data[array_size-1][y][z] = 300;
		}
	}
	printf("Malloc succeeded\n");
	int32_t neighborhood_deltas[2*NDIM][NDIM] = {{-1, 0, 0}, {0, -1, 0}, {0, 0, -1}, {0, 0, 1}, {0, 1, 0}, {1, 0, 0}};
	printf("Allocation succeeded\n");
	clock_t start = clock();
	uint32_t neighborhood[2*NDIM];
	for (int iter = 0; iter < iterations; iter++)
	{
		for (int32_t x = 0; x < array_size; x++)
		{
			for(int32_t y = 0; y < array_size; y++)
			{
				for(int32_t z = 0; z < array_size; z++)
				{
					for (int i = 0; i < (2 * NDIM); i++)
					{
						int32_t nx = x + neighborhood_deltas[i][0];
						int32_t ny = y + neighborhood_deltas[i][1];
						int32_t nz = z + neighborhood_deltas[i][2];
						nx = sClamp(nx);
						ny = sClamp(ny);
						nz = sClamp(nz);
						//printf("%d %d %d\n", nx, ny, nz);
						neighborhood[i] = data[nx][ny][nz];
					}
					kernel(neighborhood, &out[x][y][z]);
				}
			}
		}
	}
	printf("%d\r", out[3][4][5]);
	clock_t end = clock();
	float elapsed = ((float) (end - start)) / CLOCKS_PER_SEC;
	printf("Total time: %f\n", elapsed);
	return 0;
}
