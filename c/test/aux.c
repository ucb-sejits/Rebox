// <file: aux.c>

#include <stdint.h>
#include <stdlib.h>
__attribute__ ((const)) static inline size_t clamp(size_t code) {
//	size_t underflow_remainder = (~code >> 0x3cu) & 0x7u;
//	size_t overflow = (code >> 0x1eu) & underflow_remainder;
//	underflow_remainder *= 0x9249249249249249Lu;
//	overflow *= 0x9249249249249249Lu;
//	return ((code & underflow_remainder) | overflow) & 0x3fffffffu;
    code &= ~ (0x9249249249249249Lu * (code >> 0x3cu & 0x7u));
    size_t mask = code >> 0x1eu;
    code |= 0x9249249u * (mask & 0x7u);
    return code & 0x3fffffffu;
};
__attribute__ ((const)) static inline size_t add(size_t code, size_t code2) {
    return ((code >> 0 & 0x9249249249249249Lu) + (code2 >> 0 | 0x6db6db6db6db6db6u) & 0x9249249249249249Lu) << 0 | ((code >> 1 & 0x9249249249249249Lu) + (code2 >> 1 | 0x6db6db6db6db6db6u) & 0x9249249249249249Lu) << 1 | ((code >> 2 & 0x9249249249249249Lu) + (code2 >> 2 | 0x6db6db6db6db6db6u) & 0x9249249249249249Lu) << 2;
};

