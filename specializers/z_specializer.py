from __future__ import division

__author__ = 'nzhang-dev'

import ctypes

import ctree

from ctree.jit import LazySpecializedFunction, ConcreteSpecializedFunction
from ctree.c.nodes import (ArrayDef, Array, SymbolRef, Constant, FunctionDecl, MultiNode, Assign, BitAnd, BitAndAssign,
    BitShR, Deref, BitNot, ArrayRef, BitOr, BitOrAssign)

import itertools
import math
from functools import reduce

def bit_list_to_int(bit_list):
    result = 0
    for i in bit_list:
        result <<= 1
        result += i
    return result

def generateFilterMask(ndim, mask_size, ctype):
    """
    :param ndim: number of dimensions
    :param mask_size: total size of mask, in bits
    :param ctype: data type of final output
    :return: ctree.c.nodes.Array object that can function as a lookup table.
    """
    masks = []
    for bit_signature in itertools.product((0, 1), repeat=ndim):
        mask = bit_signature * int(math.ceil(mask_size / ndim))
        overflow = len(mask) - mask_size
        masks.append(Constant(bit_list_to_int(mask[overflow:])))
    array_type = ctypes.POINTER(ctype)
    return Array(type=array_type, size=2**ndim, body=masks)

def generateClamp(ndim, bits_per_dim, ctype, name):
    """
    :param ndim: number of dimensions
    :param bits_per_dim: bits per dimension
    :param ctype: ctype of data
    :param name: name of function
    :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code)
    """
    decl = FunctionDecl(name=name, params=[SymbolRef('code', sym_type=ctypes.POINTER(ctype)())])
    code = SymbolRef('code')
    mask = SymbolRef("mask")
    size = ctypes.sizeof(ctype) * 8  # 8 bits/byte
    underflow_start = Constant(size - size%ndim - ndim)
    overflow_start = Constant(ndim * bits_per_dim)
    overflow_end = Constant(underflow_start.value - 1)
    underflow_mask = SymbolRef("underflow_mask")
    overflow_mask = SymbolRef("overflow_mask")
    overflow_bits = overflow_end.value - overflow_start.value + 1
    window_mask = Constant(2 ** ndim - 1)  # ndim 1's
    overflow_window_mask = Constant(2 ** (overflow_end.value - overflow_start.value + 1) - 1)
    index_filter = Constant(2 ** (ndim * bits_per_dim) - 1)
    decl.defn = [
        BitAndAssign(
            Deref(code),
            BitNot(
                ArrayRef(
                    underflow_mask,
                    BitAnd(
                        BitShR(Deref(code), overflow_start),
                        window_mask
                    )
                )
            )
        ),
        Assign(
            SymbolRef("mask", ctype()),
            BitAnd(
                BitShR(
                    Deref(code),
                    overflow_start
                ),
                overflow_window_mask
            )
        ),
        BitOrAssign(
            Deref(code),
            ArrayRef(
                overflow_mask,
                BitAnd(
                    reduce(BitOr, [
                    BitShR(mask, Constant(i)) for i in range(0, overflow_bits, ndim)
                    ]),
                    window_mask
                )
            )
        ),
        BitAndAssign(
            Deref(code),
            index_filter
        )
    ]

    underflow_array = generateFilterMask(ndim, size, ctype)
    underflow_mask_def = ArrayDef(
        SymbolRef(underflow_mask.name, ctype(), _static=True, _const=True),
        underflow_array.size,
        underflow_array
    )

    overflow_array = generateFilterMask(ndim, ndim * bits_per_dim, ctype)
    overflow_mask_def = ArrayDef(
        SymbolRef(overflow_mask.name, ctype(), _static=True, _const=True),
        overflow_array.size,
        overflow_array
    )

    return MultiNode(
        [
            underflow_mask_def,
            overflow_mask_def,
            decl
        ]
    )

if __name__ == "__main__":
    ndim = 2
    bits_per_dim = 10
    ctype = ctypes.c_uint32
    print(generateClamp(ndim, bits_per_dim, ctype, "clamp"))