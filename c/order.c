/*
 * zorder.c
 *
 *  Created on: Feb 21, 2015
 *      Author: nzhang-dev
 */
#include <stdio.h>
#include <time.h>
#include <stdlib.h>

#ifndef DIM
#define DIM 64
#endif

#ifndef DIV
#define DIV 2
#endif

#define NEIGHBORHOOD_SIZE 9

#define standard_order(x, y) (((unsigned long) x) * DIM + y)

#define clamp(x) (x > DIM-1 ? DIM-1 : (x < 0 ? 0 : x))
#undef LT

#ifndef ORDERING
#ifndef LT
#define ORDERING "ZMB"

//https://fgiesen.wordpress.com/2009/12/13/decoding-morton-codes/

// "Insert" a 0 bit after each of the 16 low bits of x
uint32_t Part1By1(uint32_t x)
{
  x &= 0x0000ffff;                  // x = ---- ---- ---- ---- fedc ba98 7654 3210
  x = (x ^ (x <<  8)) & 0x00ff00ff; // x = ---- ---- fedc ba98 ---- ---- 7654 3210
  x = (x ^ (x <<  4)) & 0x0f0f0f0f; // x = ---- fedc ---- ba98 ---- 7654 ---- 3210
  x = (x ^ (x <<  2)) & 0x33333333; // x = --fe --dc --ba --98 --76 --54 --32 --10
  x = (x ^ (x <<  1)) & 0x55555555; // x = -f-e -d-c -b-a -9-8 -7-6 -5-4 -3-2 -1-0
  return x;
}

// "Insert" two 0 bits after each of the 10 low bits of x
static uint32_t Part1By2(uint32_t x)
{
  x &= 0x000003ff;                  // x = ---- ---- ---- ---- ---- --98 7654 3210
  x = (x ^ (x << 16)) & 0xff0000ff; // x = ---- --98 ---- ---- ---- ---- 7654 3210
  x = (x ^ (x <<  8)) & 0x0300f00f; // x = ---- --98 ---- ---- 7654 ---- ---- 3210
  x = (x ^ (x <<  4)) & 0x030c30c3; // x = ---- --98 ---- 76-- --54 ---- 32-- --10
  x = (x ^ (x <<  2)) & 0x09249249; // x = ---- 9--8 --7- -6-- 5--4 --3- -2-- 1--0
  return x;
}

static uint32_t encode(uint32_t x, uint32_t y)
{
  return (Part1By1(y) << 1) + Part1By1(x);
}




static inline uint32_t Compact1By1(uint32_t x)
{
  x &= 0x55555555;                  // x = -f-e -d-c -b-a -9-8 -7-6 -5-4 -3-2 -1-0
  x = (x ^ (x >>  1)) & 0x33333333; // x = --fe --dc --ba --98 --76 --54 --32 --10
  x = (x ^ (x >>  2)) & 0x0f0f0f0f; // x = ---- fedc ---- ba98 ---- 7654 ---- 3210
  x = (x ^ (x >>  4)) & 0x00ff00ff; // x = ---- ---- fedc ba98 ---- ---- 7654 3210
  x = (x ^ (x >>  8)) & 0x0000ffff; // x = ---- ---- ---- ---- fedc ba98 7654 3210
  return x;
}

// Inverse of Part1By2 - "delete" all bits not at positions divisible by 3
static inline uint32_t Compact1By2(uint32_t x)
{
  x &= 0x09249249;                  // x = ---- 9--8 --7- -6-- 5--4 --3- -2-- 1--0
  x = (x ^ (x >>  2)) & 0x030c30c3; // x = ---- --98 ---- 76-- --54 ---- 32-- --10
  x = (x ^ (x >>  4)) & 0x0300f00f; // x = ---- --98 ---- ---- 7654 ---- ---- 3210
  x = (x ^ (x >>  8)) & 0xff0000ff; // x = ---- --98 ---- ---- ---- ---- 7654 3210
  x = (x ^ (x >> 16)) & 0x000003ff; // x = ---- ---- ---- ---- ---- --98 7654 3210
  return x;
}

static inline uint32_t decodeX(uint32_t code)
{
  return Compact1By1(code >> 0);
}

static inline uint32_t decodeY(uint32_t code)
{
  return Compact1By1(code >> 1);
}

#else
#define ORDERING "ZLT"


#endif
#else
#undef ORDERING
#define ORDERING "STD"

uint32_t encode(uint32_t x, uint32_t y)
{
	return standard_order(x, y);
}

uint32_t decodeX(uint32_t code)
{
	return code/DIM;
}

uint32_t decodeY(uint32_t code)
{
return code % DIM;
}

#endif

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
			matrix[encode(i, j)] = (i + j)/DIV;
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
	printf("Method ");
	printf(ORDERING);
	printf("\n");
	printf("Elapsed: %f\nTotal: %llu\n", finalTime-midTime, total);
	return 0;
}
