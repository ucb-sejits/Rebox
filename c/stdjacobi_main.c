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
	uint64_t log_2_box_dim = 4;
	if (argc > 1)
	{
		array_size = atoi((const char*) argv[1]);
	}
	if(argc > 2)
	{
		log_2_box_dim = atoi((const char*) argv[2]);
	}
	int BITS = array_size;
	array_size = 1 << array_size;
	if (argc > 3)
	{
		iterations = atoi((const char*) argv[3]);
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
	uint32_t kb = 1 << log_2_box_dim;
	uint32_t jb = kb;
	printf("Box size: %u\n", kb);
	double start = omp_get_wtime();
	for (int iter = 0; iter < iterations; iter++)
	{
		#pragma omp parallel for collapse(2)
		for (uint64_t kk=0;kk<array_size;kk+=kb)
		{
			for (uint64_t jj=0;jj<array_size;jj+=jb)
			{
				for (uint64_t k=kk;k<kk+kb;k++)
				{
					for (uint64_t j=jj;j<jj+jb;j++)
					{
						for (uint64_t i=0;i<array_size;i++)
						{
							//printf("%u\t%u\t%u\n", i, j, k);
							uint32_t neighborhood[NEIGHBORS];
							for (char nindex = 0; nindex < NEIGHBORS; nindex++)
							{
								int64_t ni = neighborhood_deltas[nindex][0] + i;
								int64_t nj = neighborhood_deltas[nindex][1] + j;
								int64_t nk = neighborhood_deltas[nindex][2] + k;
								ni = sClamp(ni);
								nj = sClamp(nj);
								nk = sClamp(nk);
								//printf("%u\t%u\t%u\n", ni, nj, nk);
								uint32_t d = data[encode(ni, nj, nk)];
								//printf("%u\t%u\t%u\t%u\n", ni, nj, nk, d);
								neighborhood[nindex] = d;
							}
							out[encode(i, j, k)] = kernel(neighborhood);
							//printf("Finished kernel\n");
						}
					}
				}
			}
		}
	}
	double end = omp_get_wtime();
	dump(out, array_size * 2);
	free(data);
	free(out);
	float elapsed = ((end - start));
	printf("Total time: %f\n", elapsed);
	return 0;
}
