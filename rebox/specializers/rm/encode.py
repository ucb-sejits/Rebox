from __future__ import division, print_function
import abc
import ast
import ctypes
from functools import reduce
import operator

from ctree.c.nodes import SymbolRef, BitOr, Constant, BitShL, Mul, Add, BinaryOp
from ctree.cpp.nodes import CppDefine
import math

from rebox.specializers.order import FunctionGenerator, Ordering


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

class BitShiftEncode(Encode):
    def generate(self, ndim, bits_per_dim, ctype):
        index_params = [
            SymbolRef(name='index_{}'.format(i)) for i in range(ndim)
        ]
        params = [SymbolRef(name='index_{}'.format(i)) for i in range(ndim)]
        decl = CppDefine(
            name=self.name,
            params=index_params
        )
        shifts = [bits_per_dim] * ndim
        multipliers = [reduce(operator.add, shifts[i+1:], 0) for i in range(ndim)]
        decl.body = reduce(
            BitOr,
            [BitShL(param, Constant(multi)) for param, multi in zip(params, multipliers)]
        )

        return FunctionGenerator.GeneratedResult(decl)

class MultiplyEncode(Encode):
    def generate(self, ndim, bits_per_dim, ctype):
        index_params = [
            SymbolRef(name='index_{}'.format(i)) for i in range(ndim)
        ]
        params = [SymbolRef(name='index_{}'.format(i)) for i in range(ndim)]
        param_names = [param.name for param in params]
        decl = CppDefine(
            name=self.name,
            params=index_params
        )
        dims = [int(round(2**(bits_per_dim - 1)))] * ndim
        multipliers = [reduce(operator.mul, dims[i+1:], 1) for i in range(ndim)]
        decl.body = reduce(
            Add,
            [Mul(param, Constant(multi)) for param, multi in zip(params, multipliers)]
        )
        for node in ast.walk(decl):
            if isinstance(node, SymbolRef) and node.name in param_names:
                node._force_parentheses = True
        return FunctionGenerator.GeneratedResult(decl)

if __name__ == '__main__':
    generator = Ordering([MultiplyEncode()])
    print(generator.generate(3, math.log(10, 2), ctypes.c_uint64))
