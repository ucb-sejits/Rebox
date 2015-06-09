import abc
import ctypes

from ctree.c.nodes import FunctionDecl, SymbolRef
import ctree.c.nodes as nodes

from rebox.specializers.order import FunctionGenerator


__author__ = 'nzhang-dev'

class Add(FunctionGenerator):
    name = 'add'
    def __call__(self, index1, index2):
        return index1 + index2

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass

class BitShiftAdd(Add):
    def generate(self, ndim, bits_per_dim, ctype):
        decl = FunctionDecl(
            name=self.name,
            params=[SymbolRef('index_{}'.format(i), sym_type=ctypes.POINTER(ctype)()) for i in range(2)],
            body=[
                nodes.Add(*[SymbolRef('index_{}'.format(i)) for i in range(2)])
            ]
        )
        return FunctionGenerator.GeneratedResult(decl)