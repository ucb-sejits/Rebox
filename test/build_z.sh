#!/bin/bash
python ../specializers/z/decode.py $1 > ../c/indexing/zdecode.c
python ../specializers/z/encode.py $1 > ../c/indexing/zindex.c
gcc-4.9 -std=c11 -O2 -DSIZE=$((2**$1)) ../c/indexing/decode_timing.c -o ../c/indexing/decode_timing
echo $(../c/indexing/decode_timing)