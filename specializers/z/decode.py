from __future__ import division, print_function
import abc
import ctypes
import functools
from ctree.c.nodes import FunctionDecl, SymbolRef, Deref, Assign, BitShR, Hex, Ref, ArrayRef, BitOr, BitAnd, Constant, \
    ArrayDef, Array, AugAssign, BitAndAssign, BitXor, MultiNode, Number
from ctree.cpp.nodes import CppInclude
import math
from specializers.order import FunctionGenerator, Ordering

__author__ = 'nzhang-dev'

class Decode(FunctionGenerator):
    name = "decode"

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass

    def __call__(self, index, ndim):
        output = [0] * ndim
        binary = bin(index)[2:]
        length = len(binary)
        div, mod = divmod(length, ndim)
        padded = binary.zfill(div * ndim + mod)
        for offset in range(ndim):
            output[ndim - offset - 1] = int(padded[offset::ndim], 2)
        return output

class LUTShiftDecode(Decode):
    def generate(self, ndim, bits_per_dim, ctype):

        div, mod = divmod(bits_per_dim, ndim)  # rounded to ndim
        chunk_size = div * ndim + (ndim if mod else 0)

        def LUT_entry(num):
            binary = bin(num)[2:].zfill(chunk_size)
            chunks = [binary[i::ndim] for i in range(ndim)]
            return int(''.join(chunks), 2)

        lut = [Hex(LUT_entry(i)) for i in range(2**chunk_size)]
        LUT_def = ArrayDef(SymbolRef("decode_lut",sym_type=ctype(), _const=True), size=len(lut), body=Array(body=lut))

        function = FunctionDecl(
            name=self.name,
            params=[
                SymbolRef("code", sym_type=ctype()),
            ] + [
                SymbolRef("dim_{}".format(i), sym_type=ctypes.POINTER(ctype)()) for i in range(ndim)
            ],
        )
        function.set_inline()


        code = SymbolRef('code')
        mask_copies = int(math.ceil(chunk_size / ndim))
        mask = int(('1'.zfill(ndim))*mask_copies, 2)
        function.defn = []
        for dim in range(ndim):
            function.defn.append(
                Assign(
                    Deref(SymbolRef("dim_{}".format(dim))),
                    ArrayRef(
                        SymbolRef("decode_lut"),
                        functools.reduce(
                            BitOr,
                            [
                                BitAnd(
                                    BitShR(code, Constant(dim + chunk_num * (chunk_size - 1))), Hex(mask << chunk_num)
                                ) for chunk_num in range(ndim)
                            ]
                        )
                    )
                )
            )
        return FunctionGenerator.GeneratedResult(
            func=function,
            auxiliary=[LUT_def]
        )

class MagicBitsDecode(Decode):
    def generate(self, ndim, bits_per_dim, ctype):
        function = FunctionDecl(
            name=self.name,
            params=[
                SymbolRef("code", sym_type=ctype(), _const=True),
            ] + [
                SymbolRef("dim_{}".format(i), sym_type=ctypes.POINTER(ctype)()) for i in range(ndim)
            ],
        )
        function.set_inline()

        code = SymbolRef("code")

        dim_mask = Hex(int("1".zfill(ndim) * bits_per_dim, 2))

        adjusted_bits = int(math.ceil(math.log(bits_per_dim, 2)))
        total_bits = ndim * 2 ** adjusted_bits

        def shift_row(source_sym, target_sym, spacing, width):
            #total_bits = ndim * bits_per_dim
            total_width = spacing + width
            copies = int(math.ceil(total_bits / total_width / 2))
            keep_mask = Hex(int(("0"*spacing*2 + "1"*2*width) * copies, 2), ctype=ctypes.c_uint64())
            return Assign(
                target_sym,
                BitAnd(
                    BitXor(
                        source_sym,
                        BitShR(source_sym, Constant(spacing))
                    ),
                    keep_mask
                )
            )

        function.defn = [

        ]
        for dim in range(ndim):
            block = MultiNode()
            function.defn.append(block)
            width = 1
            spacing = ndim - 1
            block.body.append(
                SymbolRef("tmp_{}".format(dim), sym_type=ctype())
            )
            tmp = SymbolRef("tmp_{}".format(dim))
            block.body.append(
                Assign(tmp, BitAnd(BitShR(code, Constant(dim)), dim_mask))
            )
            while width <= bits_per_dim:
                print(spacing, width)
                block.body.append(
                    shift_row(tmp, tmp, spacing, width)
                )
                width *= 2
                spacing *= 2
            block.body.append(
                Assign(
                    Deref(SymbolRef("dim_{}".format(dim))),
                    tmp
                )
            )
        return FunctionGenerator.GeneratedResult(func=function)






if __name__ == '__main__':
    decode = MagicBitsDecode()
    ordering = Ordering([decode])
    print(ordering.generate(3, 8, ctypes.c_uint64))
    #print(LSD(2**30 - 1, 3))

