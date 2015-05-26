__author__ = 'nzhang-dev'

from ctree.c.nodes import Array, Constant

import ctypes
import itertools


def bit_list_to_int(bit_list):
    result = 0
    for i in bit_list:
        result <<= 1
        result += i
    return result

def decompose(z_order_code, ndim=3):
    result = [0]*ndim
    shift = 0
    dimension_shift = 0
    while z_order_code:
        for dim in range(ndim):
            result[dim] |= (z_order_code & 1) << dimension_shift
            shift += 1
            z_order_code >>= 1
        dimension_shift += 1

    return result

def generate_neighborhoods(neighborhood, ctype=ctypes.c_int32):
    """
    :param neighborhood: iterable of relative indices for neighborhood
    :return: C nested array, neighborhood elements
    """
    length = 0
    output = Array(None, None, [])
    for coord in neighborhood:
        tmp = Array(None, len(coord), [Constant(ctype(i)) for i in coord])
        length += 1
        output.body.append(tmp)
    output.size = length
    return output

def encode(indices, ctype=ctypes.c_uint32):
    indices = [ctype(i) for i in indices]
    indexes = itertools.cycle(range(len(indices)))
    shift = 0
    out = 0
    #print(indices)
    while any(indices):
        i = next(indexes)
        out |= (indices[i].value & 1) << shift
        indices[i] = ctype(indices[i].value >> 1)
        shift += 1
    return ctype(out).value

def indices(arr):
    return itertools.product(*[range(i) for i in arr.shape])

def add(coord, delta):
    return tuple(i + j for i, j in zip(coord, delta))

def clamp(coord, shape):
    return tuple(max(0, min(i, dim-1)) for i, dim in zip(coord, shape))