from __future__ import division, print_function

import abc
import ctypes
from ctree.c.nodes import MultiNode, Hex, Array, SymbolRef, FunctionDecl, Assign, BitShR, BitAnd, BitOrAssign, BitShL, \
    ArrayRef, Return, BitOr, BitNot, Constant, ArrayDef
import itertools
import math
from specializers.generic.util import bit_list_to_int
from specializers.order import FunctionGenerator

__author__ = 'nzhang-dev'


class Add(FunctionGenerator):
    name = "add"

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass

    def __call__(self, code1, code2):
        pass

class RippleCarryAdd(Add):

    def generate(self, ndim, bits_per_dim, ctype, lut_scale=1):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
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


class BitMagicAdd(Add):

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
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


class FastBitMagicAdd(Add):
    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
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


class BitMergeAdd(Add):
    """
    Uses algorithm given by http://graphics.stanford.edu/~seander/bithacks.html#MaskedMerge for complex masked merges
    """
    def generate(self, ndim, bits_per_dim, ctype):
        pass