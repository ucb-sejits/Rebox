/*
 * jacobi.c
 *
 *  Created on: Feb 26, 2015
 *      Author: nzhang-dev
 */

#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>

#include "zjacobi.c"
#include "kernel.c"


#define NDIM 3



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
	uint64_t actual_size = 1;
	for(int i = 0; i < NDIM; i++)
	{
		actual_size *= array_size;
	}
	printf("Malloccing\n");
	uint32_t *data = (uint32_t*) malloc(sizeof(uint32_t) * actual_size);
	uint32_t *out = (uint32_t*) malloc(sizeof(uint32_t) * actual_size);
	if(data == NULL)
	{
		printf("Allocation failed");
		return 1;
	}
	printf("Malloc succeeded\n");
	int64_t neighborhood_deltas[2*NDIM][NDIM] = {{-1, 0, 0}, {0, -1, 0}, {0, 0, -1}, {0, 0, 1}, {0, 1, 0}, {1, 0, 0}};
	printf("allocating delta matrix\n");
	uint64_t neighborhood_encoded_deltas[2*NDIM];
	printf("Reindexing\n");
	for (uint64_t i = 0; i < 2*NDIM; i++)
	{
		neighborhood_encoded_deltas[i] = encode(neighborhood_deltas[i]);
	}
	printf("Finished Reindexing\n");
	for (uint32_t x = 0; x < array_size; x++)
	{
		for(uint32_t y = 0; y < array_size; y++)
		{
			for(uint32_t z = 0; z < array_size; z++)
			{
				uint64_t index[] = {x, y, z};
				uint64_t addr = encode(index);
				data[addr] = 0;
				if (x == 0 || x == array_size - 1) //left and right sheets
				{
					data[addr] = 300; // arbitrary value
				}
			}
		}
	}
	printf("Allocation succeeded\n");
	clock_t start = clock();
	uint32_t neighborhood[2*NDIM];
	uint64_t delta;
	uint64_t ind;
	for (int iter = 0; iter < iterations; iter++)
	{
		for (uint64_t index = 0; index < actual_size; index++)
		{
			for (int neighborhood_index = 0; neighborhood_index < 2*NDIM; neighborhood_index++)
			{
				delta = neighborhood_encoded_deltas[neighborhood_index];
				ind = add(index, delta);
				clamp(&ind);
				neighborhood[neighborhood_index] = data[ind];
			}
			kernel(neighborhood, &out[index]);
		}
	}
	clock_t end = clock();
	float elapsed = ((float) (end - start)) / CLOCKS_PER_SEC;
	printf("Total time: %f\n", elapsed);
	return 0;
}
