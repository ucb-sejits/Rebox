from __future__ import division

__author__ = 'nzhang-dev'

import ctypes

#TODO: remove following declaration
import ctree  # forces loading of type generators. Current bug.


from ctree.c.nodes import (ArrayDef, Array, SymbolRef, Constant, FunctionDecl, MultiNode, Assign, BitAnd, BitAndAssign,
                           BitShR, Deref, BitNot, ArrayRef, BitOr, BitOrAssign, BitXor, Return, BitShL, Hex)

import itertools
import math
from functools import reduce
from util import bit_list_to_int

from specializer import OrderGenerator

class ZGenerator(OrderGenerator):


    @staticmethod
    def generate_clamp(ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code)
        """

        def _generate_repeat_mask(ndim, mask_size, ctype):
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
                masks.append(Hex(bit_list_to_int(mask[overflow:])))
            array_type = ctypes.POINTER(ctype)
            return Array(type=array_type, size=2**ndim, body=masks)

        decl = FunctionDecl(name=name, params=[SymbolRef('code', sym_type=ctypes.POINTER(ctype)())]).set_inline().set_static()
        code = SymbolRef('code')
        mask = SymbolRef("mask")
        size = ctypes.sizeof(ctype) * 8  # 8 bits/byte
        underflow_start = Hex(size - size%ndim - ndim)
        overflow_start = Hex(ndim * bits_per_dim)
        overflow_end = Hex(underflow_start.value - 1)
        underflow_mask = SymbolRef("underflow_mask")
        overflow_mask = SymbolRef("overflow_mask")
        overflow_bits = overflow_end.value - overflow_start.value + 1
        window_mask = Hex(2 ** ndim - 1)  # ndim 1's
        overflow_window_mask = Hex(2 ** (overflow_end.value - overflow_start.value + 1) - 1)
        index_filter = Hex(2 ** (ndim * bits_per_dim) - 1)
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
                            BitShR(mask, Hex(i)) for i in range(0, overflow_bits, ndim)
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

        underflow_array = _generate_repeat_mask(ndim, size, ctype)
        underflow_mask_def = ArrayDef(
            SymbolRef(underflow_mask.name, ctype(), _static=True, _const=True),
            underflow_array.size,
            underflow_array
        )

        overflow_array = _generate_repeat_mask(ndim, ndim * bits_per_dim, ctype)
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

    @staticmethod
    def generate_add(ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code, ctype code2) Adds code2 into code1
        """

        master = MultiNode()
        decl = FunctionDecl(name=name, params=[SymbolRef('code', sym_type=ctypes.POINTER(ctype)()),
                                               SymbolRef('code2', sym_type=ctype())]).set_inline().set_static()
        master.body.append(decl)
        carry_out = SymbolRef("carry_out")
        carry_in = SymbolRef("carry_in")
        original = Deref(SymbolRef("code"))
        code = SymbolRef("code_copy")
        code2 = SymbolRef("code2")

        decl.defn = [
            Assign(SymbolRef(carry_in.name, sym_type=ctype()), Constant(0)),
            Assign(SymbolRef(code.name, sym_type=ctype()), original),
            Assign(original, Constant(0))
        ]

        for shift in range(0, (bits_per_dim + 1) * ndim, ndim):
            mask = Hex((1 << ndim) - 1)
            a = BitShR(code, Hex(shift))
            b = BitShR(code2, Hex(shift))
            decl.defn.append(
                BitOrAssign(original, BitShL(BitXor(a, BitXor(b, carry_in)), Hex(shift))),
            )
            if shift != bits_per_dim * ndim:
                decl.defn.append(
                    Assign(
                        carry_in,
                        BitAnd(
                            BitOr(BitAnd(carry_in, BitOr(a, b)),
                                  BitAnd(BitNot(carry_in), BitAnd(a, b))),
                            mask
                        ),
                    ),
                )
        size = ctypes.sizeof(ctype) * 8
        return master

    @staticmethod
    def generate_encode(ndim, bits_per_dim, ctype, name, block_size=8):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :param block_size: log2 of the number of elements in the lookup table
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype indices) -> Z order index
        """
        block_size = min(block_size, bits_per_dim)
        table_size = 2**block_size
        tables = Array(type=Array(type=ctype(), size=ndim), size=table_size)
        base_table = []
        for i in range(table_size):
            binary = ("0"*(ndim - 1)).join(list(bin(i)[2:]))  # literal binary insertion
            val = int(binary, 2)
            base_table.append(val)

        for i in range(ndim):
            shifted_table = [Hex(el << i) for el in base_table]
            table_name = "lt_" + str(i)
            arr = Array(type=ctype(), size=table_size, body=shifted_table)
            tables.body.append(arr)

        table_def = ArrayDef(
            ArrayRef(
                SymbolRef("lookup_table", sym_type=ctype(), _const=True, _static=True),
                Hex(ndim)
            ),
            table_size,
            tables
        )




        decl = FunctionDecl(name=name,
                            return_type=ctype(),
                            params=[SymbolRef('indices', sym_type=ctypes.POINTER(ctype)())],
        ).set_inline().set_static()

        indices = SymbolRef("indices")

        lookup_table = SymbolRef("lookup_table")
        window = Hex(table_size - 1)

        num_windows = int(math.ceil(bits_per_dim / block_size))  # number of shifts we need to do
        things_to_or = []  # set of masks to OR together to obtain final
        for window_num in range(num_windows):  # handling 1 dimension at a time to try and preserve cache
            group = []
            for dim in range(ndim):
                shift = window_num * block_size
                item = ArrayRef(ArrayRef(lookup_table, Hex(dim)),
                                BitAnd(
                                    BitShR(
                                        ArrayRef(
                                            indices,
                                            Hex(dim)
                                        ),
                                        Hex(shift)
                                    ),
                                    window
                                )
                )
                group.append(item)
            things_to_or.append(BitShL(reduce(BitOr, group), Hex(shift)))
        reduced = reduce(BitOr, things_to_or)
        final = Return(reduced)
        decl.defn = [final]



        return MultiNode([table_def, decl])

if __name__ == "__main__":
    ndim = 4
    bits_per_dim = 6
    ctype = ctypes.c_uint32
    print(ZGenerator.generate_block(ndim, bits_per_dim, ctype))