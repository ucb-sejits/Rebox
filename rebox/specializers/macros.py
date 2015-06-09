__author__ = 'nzhang-dev'
from ctree.c.nodes import FunctionCall, SymbolRef, Constant

def prefetch(ptr, rw=0, locality=3):
    return FunctionCall(SymbolRef('__builtin_prefetch'), [ptr, Constant(rw), Constant(locality)])