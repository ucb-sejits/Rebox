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
	return result/NEIGHBORS;
}

void dump(uint32_t values[], uint32_t len)
{
	for(uint32_t i = 0; i < len; i++)
	{
		printf("%u\t", values[i]);
	}
	printf("\n");
}
