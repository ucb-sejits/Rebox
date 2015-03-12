__author__ = 'nzhang-dev'

from ctree.c.nodes import Array, Constant


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

def generate_neighborhoods(neighborhood):
    """
    :param neighborhood: iterable of relative indices for neighborhood
    :return: C nested array, neighborhood elements
    """
    length = 0
    output = Array(None, None, [])
    for coord in neighborhood:
        tmp = Array(None, len(coord), [Constant(i) for i in coord])
        length += 1
        output.body.append(tmp)
    output.size = length
    return output