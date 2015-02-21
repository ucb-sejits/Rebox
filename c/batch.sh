#!/bin/bash

gcc-4.9 -std=c99 -o "order_DLT_$1.out" order.c -DDIM="$1" -DLT
gcc-4.9 -std=c99 -o "order_DMB_$1.out" order.c -DDIM="$1"
gcc-4.9 -std=c99 -o "order_STD_$1.out" order.c -DDIM="$1" -DORDERING
