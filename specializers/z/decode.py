import abc
import ctypes
import functools
from ctree.c.nodes import FunctionDecl, SymbolRef, Deref, Assign, BitShR, Hex, Ref, ArrayRef, BitOr, BitAnd, Constant, \
    ArrayDef, Array
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

        def LUT_entry(num):
            binary = bin(num)[2:].zfill(bits_per_dim)
            chunks = [binary[i::ndim] for i in range(ndim)]
            return int(''.join(chunks), 2)

        lut = [Hex(LUT_entry(i)) for i in range(2**bits_per_dim)]
        LUT_def = ArrayDef(SymbolRef("decode_lut",sym_type=ctype()), size=2**bits_per_dim, body=Array(body=lut))

        function = FunctionDecl(
            name=self.name,
            params=[
                SymbolRef("code", sym_type=ctype(), _const=True),
            ] + [
                SymbolRef("dim_{}".format(i), sym_type=ctypes.POINTER(ctype)()) for i in range(ndim)
            ],
        )

        chunk_size = bits_per_dim
        code = SymbolRef('code')
        mask_copies = int(math.ceil(bits_per_dim / ndim))
        mask = int(('1'.zfill(ndim))*mask_copies, 2)
        function.defn = []
        for dim in range(ndim):
            function.defn.append(
                Assign(
                    Deref(SymbolRef("dim_{}".format(dim))),
                    ArrayRef(SymbolRef("decode_lut"),
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

if __name__ == '__main__':
    LSD = LUTShiftDecode()
    ordering = Ordering([LSD])
    print(ordering.generate(3, 8, ctypes.c_uint64))
    #print(LSD(2**30 - 1, 3))

