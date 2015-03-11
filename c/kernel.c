/*
 * kernel.c
 *
 *  Created on: Feb 26, 2015
 *      Author: nzhang-dev
 */

#include <stdint.h>
#include <omp.h>
#ifndef NDIM
#define NDIM 3
#endif

uint32_t kernel(uint32_t values[])
{

	uint32_t result = 0;
	for (char i = 0; i < 2*NDIM; i++)
	{
		result += values[i];
	}
	return result/(2*NDIM);
}
