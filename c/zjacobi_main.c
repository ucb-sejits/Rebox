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

#define stdEncode(x, y, z) ((x) * array_size * array_size + (y) * array_size + (z))
#define partition_to_index(partition, high, low) (high << (parallel_bits + low_order_bits) | partition << (low_order_bits) | low)

int main(int argc, char* argv[])
{
	//printf("Allocating problem\n");
	uint64_t array_size = 9;
	uint32_t iterations = 1;
	uint64_t num_threads_tmp = omp_get_max_threads();
//	num_threads_tmp = 2;
	uint64_t num_threads = 1;
	uint64_t parallel_bits = 0;
	uint64_t log_2_box_dim = 4;

	if (argc > 1)
	{
		array_size = atoi((const char*) argv[1]);
	}
	if (argc > 2)
	{
		log_2_box_dim = atoi((const char*) argv[2]);
	}
	if (argc > 3)
	{
		iterations = atoi((const char*) argv[2]);
	}
	if (argc > 4)
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
	//printf("Malloccing\n");
	uint32_t *data = (uint32_t*) malloc(sizeof(uint32_t) * actual_size);
	uint32_t *out = (uint32_t*) malloc(sizeof(uint32_t) * actual_size);
	if(data == NULL)
	{
		//printf("Allocation failed");
		return 1;
	}
	//printf("Malloc succeeded\n");
	uint64_t neighborhood_deltas[NEIGHBORS][NDIM] = {{-1L, -1L, -1L}, {-1L, -1L, 0L}, {-1L, -1L, 1L}, {-1L, 0L, -1L}, {-1L, 0L, 0L}, {-1L, 0L, 1L}, {-1L, 1L, -1L}, {-1L, 1L, 0L}, {-1L, 1L, 1L}, {0L, -1L, -1L}, {0L, -1L, 0L}, {0L, -1L, 1L}, {0L, 0L, -1L}, {0L, 0L, 0L}, {0L, 0L, 1L}, {0L, 1L, -1L}, {0L, 1L, 0L}, {0L, 1L, 1L}, {1L, -1L, -1L}, {1L, -1L, 0L}, {1L, -1L, 1L}, {1L, 0L, -1L}, {1L, 0L, 0L}, {1L, 0L, 1L}, {1L, 1L, -1L}, {1L, 1L, 0L}, {1L, 1L, 1L}};
	//printf("allocating delta matrix\n");
	uint64_t neighborhood_encoded_deltas[NEIGHBORS];

	//printf("Reindexing\n");
	for (uint64_t i = 0; i < NEIGHBORS; i++)
	{
		neighborhood_encoded_deltas[i] = encode(neighborhood_deltas[i]);
	}
	//printf("Finished Reindexing\n");
	for(uint32_t z = 0; z < array_size; z++)
	{
		uint64_t index[] = {0, 0, z};
		uint64_t addr = encode(index);
		data[addr] = 729;
	}
	//printf("Allocation succeeded\n");

	//printf("Found %d threads, %d parallel bits\n", num_threads, parallel_bits);
	const uint64_t low_order_bits = log_2_box_dim;
	//printf("Low order: %d\n", low_order_bits);
	const uint64_t low_max = 1 << low_order_bits;
	const uint64_t high_order_bits = bits*3 - parallel_bits - low_order_bits;
	//printf("High Order: %d\n", high_order_bits);
	const uint64_t high_max = 1 << high_order_bits;

	double start = omp_get_wtime();

	for (int iter = 0; iter < iterations; iter++)
	{
		//printf("Starting iteration %d\n", iter);
		//private(partition) private(neighborhood) shared(data) shared(out) shared(neighborhood_encoded_deltas)
		#pragma omp parallel for collapse(3) ordered
		for (uint64_t partition = 0; partition < num_threads; partition++)
		{
			for (uint64_t high = 0; high < high_max; high++)
			{
				for (uint64_t low = 0; low < low_max; low++)
				{
					uint32_t neighborhood[NEIGHBORS];
					uint64_t index = partition_to_index(partition, high, low);
					//printf("Index: %u\n", index);
					//printf("partition:%u\thigh:%u\tlow:%u\n", partition, high, low);

					for (uint64_t neighborhood_index = 0; neighborhood_index < NEIGHBORS; neighborhood_index++)
					{
						uint64_t delta = neighborhood_encoded_deltas[neighborhood_index];
	//					//printf("Index: %u\t", index);
						uint64_t ind = add(index, delta);
	//					//printf("ind: %u\t", ind);
						//clamp(&ind);
						ind = clamp(ind);
	//					//printf("code: %u\n", ind);
						neighborhood[neighborhood_index] = data[ind];
					}
					out[index] = kernel(neighborhood);

				}
			}
		}
	}
	double end = omp_get_wtime();

	//reusing Data as output, reordered
	for (uint32_t x = 0; x < array_size; x++)
	{
		for(uint32_t y = 0; y < array_size; y++)
		{
			for(uint32_t z = 0; z < array_size; z++)
			{
				uint64_t code[] = {x, y, z};
				uint64_t encoded = encode(code);
				data[stdEncode(x, y, z)] = out[encoded];
			}
		}
	}

	float elapsed = end - start;
	printf("%f\n", elapsed);
	//dump(data, array_size, 2);
	free(data);
	free(out);
	return 0;
}
