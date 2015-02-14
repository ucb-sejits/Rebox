__author__ = 'nzhang-dev'

import math

def z_order(*indices):
    output = 0
    stride = len(indices)
    iterations = int(math.ceil(max(math.log(index, 2) for index in indices)))
    print(iterations)
    shift = 0
    for iter_num in range(iterations):
        for index in indices:
            value = (index & (1 << iter_num)) >> iter_num  # gets the bit at that point in the binary repr.
            output |= value << shift
            shift += 1
    return output
