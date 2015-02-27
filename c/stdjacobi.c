/*
 * stdjacobi.c
 *
 *  Created on: Feb 26, 2015
 *      Author: nzhang-dev
 */

#define sClamp(x) (x < 0 ? 0 : (x > 511 ? 511 : x))
static const int BITS = 9;

static inline size_t add(size_t code, size_t code2)
{
	size_t mask = (1 << (BITS + 2)) - 1;
	int64_t x = (code >> (2*(BITS + 2))) & mask;
	int64_t x2 = (code >> (2*(BITS + 2))) & mask;
	int64_t y = (code >> (BITS + 2)) & mask;
	int64_t y2 = (code2 >> (BITS + 2)) & mask;
	int64_t z = code & mask;
	int64_t z2 = code2 & mask;

	x += x2;
	y += y2;
	z += z2;
	x = sClamp(x);
	y = sClamp(y);
	z = sClamp(z);
	return (x << (2*(BITS + 2))) | (y << (BITS + 2)) | z;
}

void clamp(size_t* code)
{
	size_t mask = (1 << (BITS + 2)) - 1;
	size_t c = *code;
	size_t x = (*code >> (2*(BITS + 2))) & mask;
	if (x >> (BITS + 2) == 1)
	{
		x = 0;
	}
	if (x >> (BITS + 1) == 1)
	{
		x = (1 << BITS) - 1;
	}

	size_t y = (*code >> (BITS + 2)) & mask;
	if (y >> (BITS + 2) == 1)
	{
		y = 0;
	}
	if (y >> (BITS + 1) == 1)
	{
		y = (1 << BITS) - 1;
	}

	size_t z = *code & mask;
	if (z >> (BITS + 2) == 1)
	{
		z = 0;
	}
	if (z >> (BITS + 1) == 1)
	{
		z = (1 << BITS) - 1;
	}
	*code = (x << (2*(BITS + 2))) | (y << (BITS + 2)) | z;
}

size_t encode(size_t* indices)
{
	return (indices[0] << (2*(BITS + 2))) | (indices[1] << (BITS + 2)) | indices[2];
}
