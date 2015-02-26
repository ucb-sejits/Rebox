/*
 * zorder.c
 *
 *  Created on: Feb 21, 2015
 *      Author: nzhang-dev
 */
#include <stdio.h>
#include <time.h>
#include <stdlib.h>

#include "zorder.c"
#include "benchmark.c"

#ifndef DIM
#define DIM 64
#endif

#define NEIGHBORHOOD_SIZE 9


int kernel(int* region) // calculates size pt average stencil
{
	int total = 0;
	for (int i = 0; i < NEIGHBORHOOD_SIZE; i++)
	{
		total += region[i];
	}
	return total/NEIGHBORHOOD_SIZE;
}

int main(int argc, char** argv)
{
	printf("Allocating\n");
	long size = DIM*DIM;
	int* matrix = (int*) malloc(size * sizeof(int));
	int neighborhood[NEIGHBORHOOD_SIZE];
	long location = 0;
	int neighborhood_indices[NEIGHBORHOOD_SIZE][2] = {{-1, -1}, {-1, 0}, {-1, 1}, {0, -1}, {0, 0}, {0, 1}, {1, -1}, {1, 0}, {1, 1}};
	unsigned long long total = 0;
	printf("Allocated\n");
	for (int i = 0; i < DIM; i++)
	{
		for (int j = 0; j < DIM; j++)
		{
			matrix[encode(i, j)] = (i + j)/2;
		}
	}
	float midTime = (float)clock()/CLOCKS_PER_SEC;
	for (uint32_t i = 0; i < size; i++)
	{
		int x = decodeX(i);
		int y = decodeY(i);
		for (int j = 0; j < NEIGHBORHOOD_SIZE; j++)
		{
			int dx = neighborhood_indices[j][0];
			int nx = clamp(x + dx);
			int dy = neighborhood_indices[j][1];
			int ny = clamp(y + dy);
			neighborhood[j] = matrix[encode(nx, ny)];
		}
		total += kernel(neighborhood);
	}

	float finalTime = (float)clock()/CLOCKS_PER_SEC;
	printf("\n");
	printf("Elapsed: %f\nTotal: %llu\n", finalTime-midTime, total);
	return 0;
}
