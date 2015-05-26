from __future__ import print_function, division

import abc
import ctypes
import math
import itertools
from ctree.c.nodes import Hex, Array, FunctionDecl, SymbolRef, BitAndAssign, BitNot, ArrayRef, BitAnd, BitShR, Assign, \
    BitOrAssign, BitOr, Return, ArrayDef, Mul
from specializers.generic.util import bit_list_to_int
from specializers.order import FunctionGenerator

__author__ = 'nzhang-dev'


class Clamp(FunctionGenerator):
    __metaclass__ = abc.ABCMeta
    name = 'clamp'

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass

    def __call__(self, coord, shape):
        return tuple(
            max(min(cd, dim-1), 0) for cd, dim in zip(coord, shape)
        )



class LUTClamp(Clamp):

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


class MulClamp(Clamp):
    name = "clamp"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
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


class PartialMulClamp(Clamp):
    name = "clamp"

    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
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