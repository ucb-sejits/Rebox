// <file: aux.c>

#include <stdint.h>
#include <stdlib.h>
__attribute__ ((const)) static inline uint64_t clamp(uint64_t code) {
//	uint64_t underflow_remainder = (~code >> 0x3cu) & 0x7u;
//	uint64_t overflow = (code >> 0x1eu) & underflow_remainder;
//	underflow_remainder *= 0x9249249249249249Lu;
//	overflow *= 0x9249249249249249Lu;
//	return ((code & underflow_remainder) | overflow) & 0x3fffffffu;
    code &= ~ (0x9249249249249249Lu * (code >> 0x3cu & 0x7u));
    uint64_t mask = code >> 0x1eu;
    code |= 0x9249249u * (mask & 0x7u);
    return code & 0x3fffffffu;
};
__attribute__ ((const)) static inline uint64_t add(uint64_t code, uint64_t code2) {
    return ((code >> 0 & 0x9249249249249249Lu) + (code2 >> 0 | 0x6db6db6db6db6db6u) & 0x9249249249249249Lu) << 0 | ((code >> 1 & 0x9249249249249249Lu) + (code2 >> 1 | 0x6db6db6db6db6db6u) & 0x9249249249249249Lu) << 1 | ((code >> 2 & 0x9249249249249249Lu) + (code2 >> 2 | 0x6db6db6db6db6db6u) & 0x9249249249249249Lu) << 2;
};

uint64_t encode(uint64_t* indices) {
    return (indices[0] & 0x1u) << 0 | (indices[1] & 0x1u) << 1 | (indices[2] & 0x1u) << 2 | (indices[0] & 0x2u) << 2 | (indices[1] & 0x2u) << 3 | (indices[2] & 0x2u) << 4 | (indices[0] & 0x4u) << 4 | (indices[1] & 0x4u) << 5 | (indices[2] & 0x4u) << 6 | (indices[0] & 0x8u) << 6 | (indices[1] & 0x8u) << 7 | (indices[2] & 0x8u) << 8 | (indices[0] & 0x10u) << 8 | (indices[1] & 0x10u) << 9 | (indices[2] & 0x10u) << 10 | (indices[0] & 0x20u) << 10 | (indices[1] & 0x20u) << 11 | (indices[2] & 0x20u) << 12 | (indices[0] & 0x40u) << 12 | (indices[1] & 0x40u) << 13 | (indices[2] & 0x40u) << 14 | (indices[0] & 0x80u) << 14 | (indices[1] & 0x80u) << 15 | (indices[2] & 0x80u) << 16 | (indices[0] & 0x100u) << 16 | (indices[1] & 0x100u) << 17 | (indices[2] & 0x100u) << 18 | (indices[0] & 0x200u) << 18 | (indices[1] & 0x200u) << 19 | (indices[2] & 0x200u) << 20 | (indices[0] & 0x400u) << 20 | (indices[1] & 0x400u) << 21 | (indices[2] & 0x400u) << 22 | (indices[0] & 0x800u) << 22 | (indices[1] & 0x800u) << 23 | (indices[2] & 0x800u) << 24 | (indices[0] & 0x1000u) << 24 | (indices[1] & 0x1000u) << 25 | (indices[2] & 0x1000u) << 26 | (indices[0] & 0x2000u) << 26 | (indices[1] & 0x2000u) << 27 | (indices[2] & 0x2000u) << 28 | (indices[0] & 0x4000u) << 28 | (indices[1] & 0x4000u) << 29 | (indices[2] & 0x4000u) << 30 | (indices[0] & 0x8000u) << 30 | (indices[1] & 0x8000u) << 31 | (indices[2] & 0x8000u) << 32 | (indices[0] & 0x10000u) << 32 | (indices[1] & 0x10000u) << 33 | (indices[2] & 0x10000u) << 34 | (indices[0] & 0x20000u) << 34 | (indices[1] & 0x20000u) << 35 | (indices[2] & 0x20000u) << 36 | (indices[0] & 0x40000u) << 36 | (indices[1] & 0x40000u) << 37 | (indices[2] & 0x40000u) << 38 | (indices[0] & 0x80000u) << 38 | (indices[1] & 0x80000u) << 39 | (indices[2] & 0x80000u) << 40 | (indices[0] & 0x100000u) << 40 | (indices[1] & 0x100000u) << 41 | (indices[2] & 0x100000u) << 42 | (indices[0] & 0x200000u) << 42 | (indices[1] & 0x200000u) << 43;
};

