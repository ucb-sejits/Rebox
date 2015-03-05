__author__ = 'nzhang-dev'

def bit_list_to_int(bit_list):
    result = 0
    for i in bit_list:
        result <<= 1
        result += i
    return result

def decompose(z_order_code, ndim):
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