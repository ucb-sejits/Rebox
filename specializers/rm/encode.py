from __future__ import division, print_function
import abc
import ctypes
from ctree.c.nodes import SymbolRef, FunctionDecl, Return, BitOr, Mul, Constant, BitShR, BitShL

from specializers.order import FunctionGenerator
from functools import reduce
import operator

__author__ = 'nzhang-dev'


class Encode(FunctionGenerator):
    name = 'encode'

    def __call__(self, indices, shape):
        return sum(
            indices[i] * reduce(operator.mul, shape[i+1:], 1) for i in range(len(indices))
        )

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass

class MultiplyEncode(Encode):
    def generate(self, ndim, bits_per_dim, ctype):
        index_params = [
            SymbolRef(name='index_{}'.format(i), sym_type=ctype()) for i in range(ndim)
        ]
        params = [SymbolRef(name='index_{}'.format(i)) for i in range(ndim)]
        decl = FunctionDecl(
            name=self.name,
            return_type=ctype(),
            params=index_params
        )
        shifts = [bits_per_dim] * ndim
        multipliers = [reduce(operator.add, shifts[i+1:], 0) for i in range(ndim)]
        decl.defn = [
            Return(
                reduce(
                    BitOr,
                    [BitShL(param, Constant(multi)) for param, multi in zip(params, multipliers)]
                )
            )
        ]
        return decl

if __name__ == '__main__':
    me = MultiplyEncode()
    print(me.generate(3, 10, ctypes.c_uint64))
