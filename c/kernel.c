/*
 * kernel.c
 *
 *  Created on: Feb 26, 2015
 *      Author: nzhang-dev
 */

#include <stdint.h>
#include <omp.h>
#ifndef NEIGHBORS
#define NEIGHBORS 27
#endif

uint32_t kernel(uint32_t values[])
{

	uint32_t result = 0;
	for (int i = 0; i < NEIGHBORS; i++)
	{
		result += values[i];
	}
	return result;
}

void dump(uint32_t values[], uint32_t row_len, uint32_t rows)
{
	for(uint32_t j = 0; j < rows; j++)
	{
		for(uint32_t i = row_len*j; i < row_len*(j+1); i++)
		{
			printf("%u\t", values[i]);
		}
		printf("\n");
	}
	printf("\n");
}
