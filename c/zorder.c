#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#define NDIM 4

#define BITS 6

#define UNDERFLOW_START (32 - 32%NDIM - NDIM)

#define OVERFLOW_START (NDIM*BITS)

#define OVERFLOW_END (UNDERFLOW_START - 1)


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

static inline uint32_t encode(uint32_t x, uint32_t y)
{
	return  Part1By1(x) | (Part1By1(y) << 1);
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

static inline uint32_t add(uint32_t a, uint32_t b)
{
    unsigned int carry = a & b;
    unsigned int result = a ^ b;
    while(carry != 0)
    {
        unsigned int shiftedcarry = carry << 2;
        carry = result & shiftedcarry;
        result ^= shiftedcarry;
    }
    return result;
}

static inline uint32_t decodeX(uint32_t code)
{
  return Compact1By1(code >> 0);
}

static inline uint32_t decodeY(uint32_t code)
{
  return Compact1By1(code >> 1);
}



static inline void clamp(uint32_t* code_ptr)
{
	//underflow has to come first, since it modifies all the bits
	uint32_t mask = (*code_ptr >> UNDERFLOW_START) & ((1 << (NDIM + 1)) - 1); ///underflow indicator bits. 1 is fine, 0 is underflow
	uint32_t final_mask = mask;
	for (int i = NDIM; i < 32; i += NDIM)
	{
		final_mask |= mask << i;
	}
	final_mask = ~final_mask;
	*code_ptr &= final_mask;
	//now for overflow.
	mask = (*code_ptr >> OVERFLOW_START) & ((1 << (OVERFLOW_END - OVERFLOW_START + 1)) - 1);
	final_mask = 0;
	for (int i = 0; i < (OVERFLOW_END - OVERFLOW_START + 1)/NDIM; i++)
	{
		final_mask |= mask & ((1 << NDIM) - 1);
		mask >>= NDIM;
	}
	mask = 0;

	for (int i = 0; i < UNDERFLOW_START; i+= NDIM)
	{
		mask |= final_mask << i;
	}
	*code_ptr |= mask;
}



//int main(int argc, const char* argv[])
//{
//	uint32_t x = 1<<13;
//	uint32_t y = 0;
//	uint32_t c = encode(x, y);
//	printf("original code: %d", c);
//	printf("\n");
//	printf("xs: %d\n", Part1By1(x));
//	printf("ys: %d\n", Part1By1(y) << 1);
//	clamp(&c);
//	printf("%d", c);
//	printf("\n");
//}
