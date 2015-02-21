__author__ = 'nzhang-dev'


import math
import itertools


def to_base(num, base):
    total = []
    while num:
        num, output = divmod(num, base)
        total.append(output)
    return reversed(total)

def z_order(indices, dimensions):
    """
    :param indices: Indices
    :param dimensions: Doesn't really matter, since z-index is dimension-agnostic
    :return: linearized index, using shift-mask method
    """
    output = 0
    length = len(indices)
    num_bits = int(math.ceil(max(math.log(index, 2) for index in indices)))
    for (offset, index), i in itertools.product(enumerate(indices), range(num_bits)):
        output |= (index & (1 << i)) << ((length - 1) * i + offset)
    return output

def regular_order(indices, dimensions):
    """
    :param indices: tuple of sought index
    :param dimensions: length of each dimension
    :return: linearized index, using successive multiply method
    """
    thickness = 1
    output = 0
    for index, depth in reversed(zip(indices, dimensions)):
        output += index * thickness
        thickness *= depth
    return output
