from __future__ import division, print_function

import abc
import ctypes
import functools
from ctree.c.nodes import FunctionDecl, SymbolRef, ArrayRef, Constant, Hex, BitOr, Return, ArrayDef, Array, Assign, Add, \
    BitAnd
import itertools
import math
from ctree.cpp.nodes import CppInclude
import sys
from specializers.generic.util import encode
from specializers.order import FunctionGenerator, Ordering

import numpy as np


__author__ = 'nzhang-dev'

class Encode(FunctionGenerator):
    name = "encode"

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass

    def __call__(self, coord):
        return int(encode(coord))

class NaiveEncode(Encode):

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
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

class SLUTEncode(FunctionGenerator):
    """
    A SLUT system encodes sections of the index as the corresponding Z-Order encoding.
    """
    name = "encode"

    @staticmethod
    def entries(ndim, ctype, pages):
        """
        :param ndim: number of dimensions
        :param ctype: type of entry 64 bit unsigned
        :return: number of entries per LUT
        """
        PAGE_SIZE = 4096
        type_size = ctypes.sizeof(ctype)
        return int(PAGE_SIZE * pages // ndim // type_size)

    def generate(self, ndim, bits_per_dim, ctype, lut_size=0, num_pages=0):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param lut_size: size of each LUT
        :param num_pages: number of pages to use (if LUT_SIZE is 0, tries to fill certain number of pages)
        :return: MultiNode with everything required, including FunctionDecl uint64_t <name> (*ctype indices) -> Z order index
        """
        if lut_size <= 0:
            if num_pages:
                lut_size = self.entries(ndim, ctype, num_pages)
            else:
                lut_size = 2**bits_per_dim
        lut_size = min(lut_size, 2**bits_per_dim)

        def encode(num, ndim):
            binary = bin(num)[2:] # binary representation of number
            split_binary = list(binary)
            interleaved = ('0'*(ndim-1)).join(split_binary)
            return int(interleaved, 2)

        def generate_LUT():
            return [encode(i, ndim) for i in range(lut_size)]

        #we want all LUTs to be contiguous in memory
        #this section allocates one huge LUT, with sections corresponding to each LUT. We'll then use some math
        #to separate it into individual LUTs
        base = generate_LUT()
        complete_LUT = [
            i << shift for shift in range(ndim) for i in base
        ]
        sym = SymbolRef("encode_LUT", sym_type=ctype(), _const=True, _static=True)
        converted = [Hex(i) for i in complete_LUT]
        LUT_def = ArrayDef(sym, lut_size * ndim, Array(body=converted))
        ("aligned(4096)",)

        start_indices = [
            Assign(
                SymbolRef("LUT_dim_{}".format(i), sym_type=ctypes.POINTER(ctype)(), _const=True, _static=True),
                Add(SymbolRef("encode_LUT"), Constant(i * lut_size))
            ) for i in range(ndim)
        ]
        params = [SymbolRef("dim_{}".format(i)) for i in range(ndim)]
        tables = [SymbolRef("LUT_dim_{}".format(i)) for i in range(ndim)]
        if lut_size >= 2**bits_per_dim:
            # single pass required, since LUT is larger than each dim
            result = functools.reduce(
                BitOr, [ArrayRef(table, param) for table, param in zip(tables, params)]
            )
        else:
            bits_at_a_time = int(np.log2(lut_size))
            mask = Hex(lut_size - 1)
            chunks = []
            num_shifts = int(math.ceil(bits_per_dim / bits_at_a_time))
            for param, table in zip(params, tables):
                for shift in range(num_shifts):
                    chunks.append(
                        ArrayRef(table, BitAnd(param >> bits_at_a_time, mask))
                    )
            result = functools.reduce(
                BitOr, chunks
            )

        function = FunctionDecl(
            ctype(),
            self.name,
            params=[SymbolRef("dim_{}".format(i), sym_type=ctype()) for i in range(ndim)],
            defn=[
                Return(result)
            ],
            attributes=('pure',)
        )
        return FunctionGenerator.GeneratedResult(
            func=function,
            auxiliary=[LUT_def]+start_indices,
            includes=(CppInclude("stdint.h"),)
        )

if __name__ == '__main__':
    ordering = Ordering([SLUTEncode()])
    print(ordering.generate(3, int(sys.argv[1]), ctypes.c_uint64))