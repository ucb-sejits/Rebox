import abc
import ctypes

from ctree.c.nodes import Hex, FunctionDecl, SymbolRef, Assign, Ref, BitShR, Number, And

from rebox.specializers.order import FunctionGenerator


__author__ = 'nzhang-dev'


class Decode(FunctionGenerator):
    name = "decode"

    def __call__(self, index, bits_per_dim, ndim):
        return [(index >> (shift*bits_per_dim)) % (2**bits_per_dim) for shift in range(ndim)]

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass


class MaskedDecode(FunctionGenerator):
    def generate(self, ndim, bits_per_dim, ctype):
        mask = Hex(2**ndim - 1)
        func = FunctionDecl(
            name=self.name,
            params=[SymbolRef('code', sym_type=ctype())] + [
                SymbolRef('index_{}'.format(i), sym_type=ctypes.POINTER(ctype)()) for i in range(ndim)
            ],
        )
        statements = [
            Assign(
                Ref(SymbolRef('index_{}'.format(i))),
                And(BitShR(SymbolRef('code'), Number(bits_per_dim * ndim)), mask)
            ) for i in range(ndim)
        ]
        func.defn = statements
        return FunctionGenerator(func=func)