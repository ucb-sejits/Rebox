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
#include <omp.h>

#define NDIM 3

#include "kernel.c"


#define sClamp(x) (x < 0 ? 0 : ((x < array_size) ? x : array_size - 1))
#define encode(x, y, z) ((x) * array_size * array_size + (y) * array_size + (z))

int main(int argc, char* argv[])
{


	printf("Allocating problem\n");
	uint64_t array_size = 9;
	uint32_t iterations = 1;
	if (argc > 1)
	{
		array_size = atoi((const char*) argv[1]);
	}
	int BITS = array_size;
	array_size = 1 << array_size;
	if (argc > 2)
	{
		iterations = atoi((const char*) argv[2]);
	}
	uint64_t actual_size = 1;
	for(int i = 0; i < NDIM; i++)
	{
		actual_size *= array_size;
	}
	printf("Malloccing: %d\n", actual_size);
	uint32_t* data = (uint32_t*) malloc(sizeof(uint32_t) * actual_size);
	uint32_t* out = (uint32_t*) malloc(sizeof(uint32_t) * actual_size);
	printf("Malloc'd\n");
	//printf("%ul\t%ul\n", data, out);
	if(!out || !data)
	{
		printf("Allocation failed");
		return 1;
	}
	printf("filling in data\n");
	for (uint64_t i = 0; i < array_size; i++)
	{
		data[i] = 729; ///x = y = 0, z = i -> 729
	}
	for(uint64_t i = array_size; i < actual_size - array_size; i++)
	{
		data[i] = 0;
	}
	//dump(out, array_size * 2);
	printf("Malloc succeeded\n");
	uint64_t neighborhood_deltas[NEIGHBORS][NDIM] = {{-1L, -1L, -1L}, {-1L, -1L, 0L}, {-1L, -1L, 1L}, {-1L, 0L, -1L}, {-1L, 0L, 0L}, {-1L, 0L, 1L}, {-1L, 1L, -1L}, {-1L, 1L, 0L}, {-1L, 1L, 1L}, {0L, -1L, -1L}, {0L, -1L, 0L}, {0L, -1L, 1L}, {0L, 0L, -1L}, {0L, 0L, 0L}, {0L, 0L, 1L}, {0L, 1L, -1L}, {0L, 1L, 0L}, {0L, 1L, 1L}, {1L, -1L, -1L}, {1L, -1L, 0L}, {1L, -1L, 1L}, {1L, 0L, -1L}, {1L, 0L, 0L}, {1L, 0L, 1L}, {1L, 1L, -1L}, {1L, 1L, 0L}, {1L, 1L, 1L}};
	printf("Allocation succeeded\n");
	double start = omp_get_wtime();
	uint32_t neighborhood[NEIGHBORS];
	for (int iter = 0; iter < iterations; iter++)
	{
		#pragma omp parallel for num_threads(omp_get_num_threads())
		for (uint64_t i = 0; i < actual_size; i++)
		{
			int32_t x = i >> (BITS * 2);
			int32_t y = (i >> BITS) & ((1 << BITS) - 1);
			int32_t z = i & ((1 << BITS) - 1);

			for (int i = 0; i < NEIGHBORS; i++)
			{
				int32_t nx = x + neighborhood_deltas[i][0];
				int32_t ny = y + neighborhood_deltas[i][1];
				int32_t nz = z + neighborhood_deltas[i][2];
				nx = sClamp(nx);
				ny = sClamp(ny);
				nz = sClamp(nz);
				neighborhood[i] = data[encode(nx, ny, nz)];
			}
			out[encode(x, y, z)] = kernel(neighborhood);
			//printf("%u\t", out[encode(x,y,z)]);
		}
	}
	double end = omp_get_wtime();
	dump(out, array_size * 2);
	float elapsed = ((end - start));
	printf("Total time: %f\n", elapsed);
	return 0;
}
