/*
 * kernel.c
 *
 *  Created on: Feb 26, 2015
 *      Author: nzhang-dev
 */

#include <stdint.h>
#ifndef NDIM
#define NDIM 3
#endif

void kernel(uint32_t values[], uint32_t* out)
{
	uint32_t result = 0;
	for (char i = 0; i < 2*NDIM; i++)
	{
		result += values[i];
	}
	*out = result/(2*NDIM);
}
