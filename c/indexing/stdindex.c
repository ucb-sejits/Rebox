#include <stdint.h>

__attribute__((pure)) static inline size_t encode(size_t x, size_t y, size_t z) {
	return (x << 20) | (y << 10) | z;
}
