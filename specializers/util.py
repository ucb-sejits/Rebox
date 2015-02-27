__author__ = 'nzhang-dev'

def bit_list_to_int(bit_list):
    result = 0
    for i in bit_list:
        result <<= 1
        result += i
    return result