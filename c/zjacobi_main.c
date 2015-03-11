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
#include <omp.h>

#include "zjacobi.c"
#include "kernel.c"


#define NDIM 3

int main(int argc, char* argv[])
{
	printf("Allocating problem\n");
	uint64_t array_size = 9;
	uint32_t iterations = 1;
	uint64_t num_threads_tmp = omp_get_max_threads();
//	num_threads_tmp = 2;
	uint64_t num_threads = 1;
	uint64_t parallel_bits = 0;

	if (argc > 1)
	{
		array_size = atoi((const char*) argv[1]);
	}
	if (argc > 2)
	{
		iterations = atoi((const char*) argv[2]);
	}
	if (argc > 3)
	{
		num_threads_tmp = atoi((const char*) argv[3]);
	}

	while (num_threads < num_threads_tmp)
	{
		num_threads <<= 1;
		parallel_bits++;
	}
	if (num_threads > num_threads_tmp)
	{
		num_threads >>= 1;
		parallel_bits--;
	}
	int bits = array_size;
	array_size = 1 << array_size;
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
	for (int i = 0; i < 2*NDIM; i++)
	{
		printf("%d\t", neighborhood_encoded_deltas[i]);
	}
	printf("\n");
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

	printf("Found %d threads, %d parallel bits\n", num_threads, parallel_bits);
	double start = omp_get_wtime();
	//printf("Start time: %f", start/CLOCKS_PER_SEC);

	for (int iter = 0; iter < iterations; iter++)
	{
		printf("Starting iteration %d\n", iter);
		//private(partition) private(neighborhood) shared(data) shared(out) shared(neighborhood_encoded_deltas)
		#pragma omp parallel for ordered num_threads(num_threads)

		for (uint64_t partition = 0; partition < num_threads; partition++)
		{
			uint32_t neighborhood[2*NDIM];
			uint64_t partition_mask = partition << ((bits*NDIM) - parallel_bits);
			for (uint64_t i = 0; i < (actual_size >> parallel_bits); i++)
			{

				uint64_t index = i | partition_mask;
				//printf("i: %u\tpartition:%u\tindex:%d\n", i, partition, index);
				//#pragma omp critical
				{
				for (uint64_t neighborhood_index = 0; neighborhood_index < 2*NDIM; neighborhood_index++)
				{
					//printf("e");
					//fflush(stdout);
					uint64_t delta = neighborhood_encoded_deltas[neighborhood_index];
					uint64_t ind = add(index, delta);
					clamp(&ind);
					//printf("p");
					//fflush(stdout);
					neighborhood[neighborhood_index] = data[ind];
				}
				}
				out[index] = kernel(neighborhood);

			}

		}
	}
	double end = omp_get_wtime();
	//printf("End time: %f", end/CLOCKS_PER_SEC);
	float elapsed = end - start;
	printf("Total time: %f\n", elapsed);
	free(data);
	free(out);
	return 0;
}
