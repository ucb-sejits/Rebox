
#include <stdlib.h>
#include <stdint.h>
inline void decode(const size_t code, size_t* dim_0, size_t* dim_1, size_t* dim_2) {
    
    size_t tmp_0;
    tmp_0 = code >> 0 & 0x249249u;
    tmp_0 = (tmp_0 ^ tmp_0 >> 2) & 0xc30c3lu;
    tmp_0 = (tmp_0 ^ tmp_0 >> 4) & 0xf00flu;
    tmp_0 = (tmp_0 ^ tmp_0 >> 8) & 0xfflu;
    tmp_0 = (tmp_0 ^ tmp_0 >> 16) & 0xfffflu;
    * dim_0 = tmp_0;

    
    size_t tmp_1;
    tmp_1 = code >> 1 & 0x249249u;
    tmp_1 = (tmp_1 ^ tmp_1 >> 2) & 0xc30c3lu;
    tmp_1 = (tmp_1 ^ tmp_1 >> 4) & 0xf00flu;
    tmp_1 = (tmp_1 ^ tmp_1 >> 8) & 0xfflu;
    tmp_1 = (tmp_1 ^ tmp_1 >> 16) & 0xfffflu;
    * dim_1 = tmp_1;

    
    size_t tmp_2;
    tmp_2 = code >> 2 & 0x249249u;
    tmp_2 = (tmp_2 ^ tmp_2 >> 2) & 0xc30c3lu;
    tmp_2 = (tmp_2 ^ tmp_2 >> 4) & 0xf00flu;
    tmp_2 = (tmp_2 ^ tmp_2 >> 8) & 0xfflu;
    tmp_2 = (tmp_2 ^ tmp_2 >> 16) & 0xfffflu;
    * dim_2 = tmp_2;

};

