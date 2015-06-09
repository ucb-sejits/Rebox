import abc

from ctree.c.nodes import FunctionDecl, SymbolRef, Return

from rebox.specializers.order import FunctionGenerator


__author__ = 'nzhang-dev'

class Clamp(FunctionGenerator):
    name = 'clamp'
    def __call__(self, index, bounds):
        return tuple(max(0, min(i, bound)) for i, bound in zip(index, bounds))

    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        pass


class SimpleClamp(Clamp):
    def generate(self, ndim, bits_per_dim, ctype):
        return FunctionDecl(
            return_type=ctype(),
            params=[SymbolRef('index', sym_type=ctype())],
            defn=[
                Return(SymbolRef('index'))
            ]
        )