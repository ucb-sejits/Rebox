from __future__ import division

__author__ = 'nzhang-dev'

import ctypes

import ctree

from ctree.jit import LazySpecializedFunction, ConcreteSpecializedFunction
from ctree.c.nodes import (ArrayDef, Array, SymbolRef, Constant, FunctionDecl, MultiNode, Assign, BitAnd, BitAndAssign,
    BitShR, Deref, BitNot, ArrayRef, BitOr, BitOrAssign, Add)

import itertools
import math
from functools import reduce

def bit_list_to_int(bit_list):
    result = 0
    for i in bit_list:
        result <<= 1
        result += i
    return result

def generateRepeatMask(ndim, mask_size, ctype):
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

    underflow_array = generateRepeatMask(ndim, size, ctype)
    underflow_mask_def = ArrayDef(
        SymbolRef(underflow_mask.name, ctype(), _static=True, _const=True),
        underflow_array.size,
        underflow_array
    )

    overflow_array = generateRepeatMask(ndim, ndim * bits_per_dim, ctype)
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


def generateAdd(ndim, bits_per_dim, ctype, name):
    """
    :param ndim: number of dimensions
    :param bits_per_dim: bits per dimension
    :param ctype: ctype of data
    :param name: name of function
    :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code, ctype code2) Adds code2 into code1
    """

    master = MultiNode()
    decl = FunctionDecl(name=name, params=[SymbolRef('code', sym_type=ctypes.POINTER(ctype)()),
                                           SymbolRef('code2', sym_type=ctype())])


    size = ctypes.sizeof(ctype) * 8

    original = Deref(SymbolRef("code"))
    code = SymbolRef("code_copy")
    code2 = SymbolRef("code2")
    masked_code = SymbolRef("masked_code")
    masked_code2 = SymbolRef("masked_code2")
    repeat_mask_array = SymbolRef("repeat_mask_array")

    repeat_mask = []
    for i in range(ndim):
        s = [0]*ndim
        s[i] = 1
        s *= int(size / ndim) + 1
        s = s[(len(s) - size):]
        repeat_mask.append(Constant(bit_list_to_int(s)))

    repeat_mask.reverse()
    repeat_mask = Array(type=ctype, size=ndim, body=repeat_mask)


    decl.defn = [
            Assign(SymbolRef("code_copy", ctype()), Deref(SymbolRef("code"))),
            Assign(original, Constant(0)),
            SymbolRef("masked_code", ctype()),
            SymbolRef("masked_code2", ctype()),
        ]


    for i in range(ndim):
        position = 2 ** i
        # index of first element of ith dimension
        decl.defn.extend([
            Assign(masked_code,  # set non-X bits to 1
                   BitOr(
                       code,
                       BitNot(
                           ArrayRef(repeat_mask_array, Constant(i))
                       )
                   )
            ),
            Assign(masked_code2,  # set non-X bits to 0
                   BitAnd(
                       code2,
                       ArrayRef(repeat_mask_array, Constant(i))
                   )
            ),
            BitOrAssign(original,
                        BitAnd(
                            Add(masked_code, masked_code2),
                            ArrayRef(repeat_mask_array,
                                Constant(i)
                            )
                        )
            ),
        ])

    master.body = [
        ArrayDef(SymbolRef(repeat_mask_array.name, ctype(), _static=True, _const=True),
                 repeat_mask.size,
                 repeat_mask),
        decl
    ]
    return master

if __name__ == "__main__":
    ndim = 4
    bits_per_dim = 6
    ctype = ctypes.c_uint32
    print(generateClamp(ndim, bits_per_dim, ctype, "clamp"))
    print(generateAdd(ndim, bits_per_dim, ctype, "add"))