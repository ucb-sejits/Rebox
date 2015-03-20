from __future__ import division, print_function

__author__ = 'nzhang-dev'

import ctypes
import sys

#TODO: remove following declaration


from ctree.c.nodes import (ArrayDef, Array, SymbolRef, FunctionDecl, Constant, MultiNode, Assign, BitAnd, BitAndAssign,
                           BitShR, BitNot, ArrayRef, BitOr, BitOrAssign, Add, Return, BitShL, Hex, Mul)

import itertools
import math
from functools import reduce
from util import bit_list_to_int

from order import FunctionGenerator, Ordering


class LUTClamp(FunctionGenerator):
    name = "clamp"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code)
        """

        def _generate(ndim, mask_size, ctype):
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

        decl = FunctionDecl(name=self.name, params=[SymbolRef('code', sym_type=ctype())], return_type=ctype(),
                            attributes=('pure',))
        code = SymbolRef('code')
        mask = SymbolRef("mask")
        size = ctypes.sizeof(ctype) * 8  # 8 bits/byte
        underflow_start = Hex(size - size%ndim - ndim)
        overflow_start = Hex(ndim * bits_per_dim)
        overflow_end = Hex(underflow_start.value - 1)
        underflow_mask = SymbolRef(self.name + "_underflow_mask")
        overflow_mask = SymbolRef(self.name + "_overflow_mask")
        overflow_bits = overflow_end.value - overflow_start.value + 1
        window_mask = Hex(2 ** ndim - 1)  # ndim 1's
        overflow_window_mask = Hex(2 ** (overflow_end.value - overflow_start.value + 1) - 1)
        index_filter = Hex(2 ** (ndim * bits_per_dim) - 1)
        decl.defn = [
            BitAndAssign(
                code,
                BitNot(
                    ArrayRef(
                        underflow_mask,
                        BitAnd(
                            BitShR(code, underflow_start),
                            window_mask
                        )
                    )
                )
            ),
            Assign(
                SymbolRef("mask", ctype()),
                BitAnd(
                    BitShR(
                        code,
                        overflow_start
                    ),
                    overflow_window_mask
                )
            ),
            BitOrAssign(
                code,
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
            Return(
                BitAnd(
                    code,
                    index_filter
                )
            )
        ]

        underflow_array = _generate(ndim, size, ctype)
        underflow_mask_def = ArrayDef(
            SymbolRef(underflow_mask.name, ctype(), _const=True),
            underflow_array.size,
            underflow_array
        )

        overflow_array = _generate(ndim, ndim * bits_per_dim, ctype)
        overflow_mask_def = ArrayDef(
            SymbolRef(overflow_mask.name, ctype(), _const=True),
            overflow_array.size,
            overflow_array
        )
        decl.set_static()
        decl.set_inline()

        return FunctionGenerator.GeneratedResult(decl, [underflow_mask_def, overflow_mask_def])

class Add2(FunctionGenerator):
    name = "add"

    def generate(self, ndim, bits_per_dim, ctype, lut_scale=1):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :param lut_scale: lookup table scale -> how many chunks are we looking at each time?
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code, ctype code2) Adds code2 into code1
        """

        master = MultiNode()
        block_size = lut_scale * ndim  # bits in a block
        block_space = 2**block_size
        carry_lookup_table = [[[0]*block_space for _ in range(block_space)] for _ in range(block_space)] # ndim^3 lookup table
        output_lookup_table = [[[0]*block_space for _ in range(block_space)] for _ in range(block_space)]

        for chunk0, chunk1, carry in itertools.product(range(block_space), repeat=3):
            # each chunk is responsible for block_space bits
            binary = [[int(i) for i in bin(j)[2:].zfill(block_size)] for j in (chunk0, chunk1, carry)]
            bit_aligned = zip(*binary)  # reorders binary so that same bits are in each sublist
            sums = [sum(bits) for bits in bit_aligned]
            carry_bits = [s // 2 for s in sums]
            output_bits = [s % 2 for s in sums]
            carry_lookup_table[chunk0][chunk1][carry] = Hex(bit_list_to_int(carry_bits))
            output_lookup_table[chunk0][chunk1][carry] = Hex(bit_list_to_int(output_bits))

        arrays = []
        for arr in carry_lookup_table:
            sub_arrays = []
            for sub_arr in arr:
                sub_arrays.append(Array(type=ctype, size=block_space, body=sub_arr))
            arrays.append(Array(type=Array(type=ctype, size=block_space), size=block_space, body=sub_arrays))
        carry_array = Array(type=Array(type=Array(type=ctype, size=block_space), size=block_space), size=block_space,
                            body=arrays)

        arrays = []
        for arr in output_lookup_table:
            sub_arrays = []
            for sub_arr in arr:
                sub_arrays.append(Array(type=ctype, size=block_space, body=sub_arr))
            arrays.append(Array(type=Array(type=ctype, size=block_space), size=block_space, body=sub_arrays))
        output_array = Array(type=Array(type=Array(type=ctype, size=block_space), size=block_space), size=block_space,
                            body=arrays)


        carry_table = SymbolRef(self.name + "_carry_table")
        output_table = SymbolRef(self.name + "_output_table")



        decl = FunctionDecl(name=self.name,
                            return_type=ctype(),
                            params=[SymbolRef('code', sym_type=ctype()),
                                    SymbolRef('code2', sym_type=ctype()),],
                            attributes=('pure',)
        )
        master.body.append(decl)
        carry_in = SymbolRef("carry_in")
        code = SymbolRef("code")
        out = SymbolRef("out")
        code2 = SymbolRef("code2")
        size = ctypes.sizeof(ctype) * 8
        decl.defn = [
            Assign(SymbolRef(carry_in.name, sym_type=ctype()), Hex(0)),
            Assign(SymbolRef(out.name, sym_type=ctype()), Hex(0))
        ]
        shifts = int(math.ceil(size/lut_scale))
        mask = Hex(block_space - 1)
        for shift in range(0, size, ndim*lut_scale):
            masked_code = BitAnd(BitShR(code, Hex(shift)), mask)
            masked_code2 = BitAnd(BitShR(code2, Hex(shift)), mask)
            decl.defn.append(
                BitOrAssign(out,
                            BitShL(
                                ArrayRef(
                                    ArrayRef(
                                        ArrayRef(
                                            output_table,
                                            masked_code
                                        ),
                                        masked_code2
                                    ),
                                    carry_in
                                ),
                                Hex(shift)
                            )
                )
            )
            if shift != size - 1:
                decl.defn.append(
                    Assign(carry_in,
                           ArrayRef(
                               ArrayRef(
                                   ArrayRef(
                                       carry_table,
                                       masked_code
                                   ),
                                   masked_code2
                               ),
                               carry_in
                           )
                    )
                )
        decl.defn.append(
            Return(out)
        )

        decl.set_static()
        decl.set_inline()

        return FunctionGenerator.GeneratedResult(decl, [
            Assign(
                ArrayRef(
                    ArrayRef(
                        ArrayRef(
                            SymbolRef(
                                carry_table.name,
                                sym_type=ctype()
                            ),
                            Hex(block_space)
                        ),
                        Hex(block_space)
                    ),
                    Hex(block_space)
                ),
                carry_array
            ),
            Assign(
                ArrayRef(
                    ArrayRef(
                        ArrayRef(
                            SymbolRef(
                                output_table.name,
                                sym_type=ctype()
                            ),
                            Hex(block_space)
                        ),
                        Hex(block_space)
                    ),
                    Hex(block_space)
                ),
                output_array
            )
        ])

class Encode(FunctionGenerator):
    name = "encode"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype indices) -> Z order index
        """
        size = ctypes.sizeof(ctype) * 8  # bit size of type
        decl = FunctionDecl(name=self.name, params=[SymbolRef('indices', sym_type=ctypes.POINTER(ctype)())],
                            return_type=ctype())
        indices = SymbolRef('indices')
        shifts = range(int(math.ceil(size/ndim)) + 1)
        steps = []
        for shift, index in itertools.product(shifts, range(ndim)):
            if ndim*shift + index > size:
                break
            ind = ArrayRef(indices, Constant(index))
            elt = ind & Hex(2**shift)
            final_value = elt << Constant((ndim-1)*shift + index)
            steps.append(final_value)
        retval = reduce(BitOr, steps)
        decl.defn = [Return(retval)]
        return FunctionGenerator.GeneratedResult(decl)



class Add3(FunctionGenerator):
    name = "add"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code, ctype code2) Adds code2 into code1
        """

        master = MultiNode()
        decl = FunctionDecl(name=self.name, params=[SymbolRef('code', sym_type=ctype()),
                                               SymbolRef('code2', sym_type=ctype())],
                            return_type=ctype(), attributes=('pure',))


        size = ctypes.sizeof(ctype) * 8

        code = SymbolRef("code")
        code2 = SymbolRef("code2")
        ret = SymbolRef("output")
        masked_code = SymbolRef("masked_code")
        masked_code2 = SymbolRef("masked_code2")
        repeat_mask_array = SymbolRef(self.name + "_repeat_mask_array")

        repeat_mask = []
        for i in range(ndim):
            s = [0]*ndim
            s[i] = 1
            s *= int(size / ndim) + 1
            s = s[(len(s) - size):]
            repeat_mask.append(Hex(bit_list_to_int(s)))

        repeat_mask.reverse()
        repeat_mask = Array(type=ctype, size=ndim, body=repeat_mask)


        decl.defn = [
                Assign(SymbolRef(ret.name, ctype()), Constant(0)),
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
                               ArrayRef(repeat_mask_array, Hex(i))
                           )
                       )
                ),
                Assign(masked_code2,  # set non-X bits to 0
                       BitAnd(
                           code2,
                           ArrayRef(repeat_mask_array, Hex(i))
                       )
                ),
                BitOrAssign(ret,
                            BitAnd(
                                Add(masked_code, masked_code2),
                                ArrayRef(repeat_mask_array,
                                    Hex(i)
                                )
                            )
                ),
            ])

        decl.defn.append(
            Return(ret)
        )
        decl.set_static()
        decl.set_inline()

        return FunctionGenerator.GeneratedResult(decl, [ArrayDef(SymbolRef(repeat_mask_array.name, ctype(), _const=True),
                     repeat_mask.size,
                     repeat_mask)])

class Add4(FunctionGenerator):
    name = "add"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code, ctype code2) Adds code2 into code1
        """

        master = MultiNode()
        decl = FunctionDecl(name=self.name, params=[SymbolRef('code', sym_type=ctype()),
                                               SymbolRef('code2', sym_type=ctype())],
                            return_type=ctype(), attributes=["const"])


        size = ctypes.sizeof(ctype) * 8

        code = SymbolRef("code")
        code2 = SymbolRef("code2")

        repeat = int(math.ceil(size / ndim))
        overflow = repeat*ndim - size

        dim_mask_str = "1".rjust(ndim, "0")*repeat
        dim_mask = Hex(int(dim_mask_str[overflow:], 2))

        inverted_mask_str = "0".rjust(ndim, "1")*repeat
        inverted_mask = Hex(int(inverted_mask_str[overflow:], 2))

        to_be_combined = []

        for shift in range(ndim):
            shifted_code = code >> shift
            shifted_code2 = code2 >> shift
            result = ((shifted_code & dim_mask) + (shifted_code2 | inverted_mask)) & dim_mask
            to_be_combined.append(result << shift)

        decl.defn.append(
            Return(reduce(BitOr, to_be_combined))
        )
        decl.set_inline()
        decl.set_static()

        return FunctionGenerator.GeneratedResult(decl)

class MulClamp(FunctionGenerator):
    name = "clamp"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code)
        """
        decl = FunctionDecl(name=self.name, params=[SymbolRef('code', sym_type=ctype())], return_type=ctype(),
                            attributes=("const",))
        code = SymbolRef('code')
        mask = SymbolRef("mask")
        size = ctypes.sizeof(ctype) * 8  # 8 bits/byte
        underflow_start = Hex(size - size%ndim - ndim)
        overflow_start = Hex(ndim * bits_per_dim)
        overflow_end = Hex(underflow_start.value - 1)
        overflow_bits = overflow_end.value - overflow_start.value + 1
        window_mask = Hex(2 ** ndim - 1)  # ndim 1's
        overflow_window_mask = Hex(2 ** (overflow_end.value - overflow_start.value + 1) - 1)
        index_filter = Hex(2 ** (ndim * bits_per_dim) - 1)

        repeater = "1".zfill(ndim) * size
        overflow = Hex(int(repeater[-overflow_start.value:], 2))
        underflow = Hex(int(repeater[-size:], 2))

        decl.defn = [
            BitAndAssign(
                code,
                BitNot(
                    Mul(
                        underflow,
                        BitAnd(
                            BitShR(code, underflow_start),
                            window_mask
                        )
                    )
                )
            ),
            Assign(
                SymbolRef("mask", ctype()),
                BitAnd(
                    BitShR(
                        code,
                        overflow_start
                    ),
                    overflow_window_mask
                )
            ),
            BitOrAssign(
                code,
                Mul(
                    overflow,
                    BitAnd(
                        reduce(BitOr, [
                            BitShR(mask, Hex(i)) for i in range(0, overflow_bits, ndim)
                        ]),
                        window_mask
                    )
                )
            ),
            Return(
                BitAnd(
                    code,
                    index_filter
                )
            )
        ]

        decl.set_inline()
        decl.set_static()

        return FunctionGenerator.GeneratedResult(decl)


class PartialMulClamp(FunctionGenerator):
    name = "clamp"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype code)
        """
        decl = FunctionDecl(name=self.name, params=[SymbolRef('code', sym_type=ctype())], return_type=ctype(),
                            attributes=("const",))
        code = SymbolRef('code')
        mask = SymbolRef("mask")
        size = ctypes.sizeof(ctype) * 8  # 8 bits/byte
        underflow_start = Hex(size - size%ndim - ndim)
        overflow_start = Hex(ndim * bits_per_dim)
        overflow_end = Hex(underflow_start.value - 1)
        overflow_bits = overflow_end.value - overflow_start.value + 1
        window_mask = Hex(2 ** ndim - 1)  # ndim 1's
        overflow_window_mask = Hex(2 ** (overflow_end.value - overflow_start.value + 1) - 1)
        index_filter = Hex(2 ** (ndim * bits_per_dim) - 1)

        repeater = "1".zfill(ndim) * size
        overflow = Hex(int(repeater[-overflow_start.value:], 2))
        underflow = Hex(int(repeater[-size:], 2))

        decl.defn = [
            BitAndAssign(
                code,
                BitNot(
                    Mul(
                        underflow,
                        BitAnd(
                            BitShR(code, underflow_start),
                            window_mask
                        )
                    )
                )
            ),
            Assign(
                SymbolRef("mask", ctype()),
                BitAnd(
                    BitShR(
                        code,
                        overflow_start
                    ),
                    overflow_window_mask
                )
            ),
            BitOrAssign(
                code,
                Mul(
                    overflow,
                    BitAnd(mask, Hex(2**ndim - 1))
                )
            ),
            Return(
                BitAnd(
                    code,
                    index_filter
                )
            )
        ]

        decl.set_inline()
        decl.set_static()

        return FunctionGenerator.GeneratedResult(decl)

class BitMergeAdd(FunctionGenerator):
    """
    Uses algorithm given by http://graphics.stanford.edu/~seander/bithacks.html#MaskedMerge for complex masked merges
    """
    name = "add"
    def generate(self, ndim, bits_per_dim, ctype):
        pass

if __name__ == "__main__":
    #print(sys.argv)
    ndim = 3
    if len(sys.argv) > 1:
        ndim = int(sys.argv[1])
    bits_per_dim = 12
    if len(sys.argv) > 2:
        bits_per_dim = int(sys.argv[2])
    ctype = ctypes.c_uint64
    add_choice, clamp_choice = sys.argv[3:5]
    a = [Add2, Add3, Add4][int(add_choice)]
    c = [LUTClamp, MulClamp, PartialMulClamp][int(clamp_choice)]

    generator = Ordering([a(), c(), Encode()])

    print(generator.generate(ndim, bits_per_dim, ctype))