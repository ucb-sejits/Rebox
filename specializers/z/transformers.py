import ast
import copy
import ctypes

from ctree.c.nodes import For, Assign, SymbolRef, Lt, Number, PostInc, MultiNode
import numpy as np

from specializers.generic import DeltaRenamer, SymbolReplacer
from specializers.generic.util import encode


__author__ = 'nzhang-dev'

class IndexTransformer(ast.NodeTransformer):
    def __init__(self, namespace, ctype=ctypes.c_uint):
        self.namespace = namespace
        self.ctype = ctype

    def visit_For(self, node):
        body = [self.visit(i) for i in node.body]
        if not (isinstance(node, ast.For) and isinstance(node.iter, ast.Call) and node.iter.func.id == "indices"):
            node.body = body
            return node
        shapes = self.namespace[node.iter.args[0].id].shape
        out = For(init=Assign(SymbolRef(node.target.id, sym_type=self.ctype()), Number(0, ctype=self.ctype)),
                  test=Lt(SymbolRef(node.target.id), Number(np.multiply.reduce(shapes))),
                  incr=PostInc(SymbolRef(node.target.id)),
                  body=body)
        return out

class DeltaTransformer(ast.NodeTransformer):
    def __init__(self, namespace=None, ndim=3):
        self.namespace = namespace if namespace is not None else {}
        self.ndim = ndim
    def visit_For(self, node):
        body = [self.visit(i) for i in node.body]
        if not (isinstance(node, ast.For) and isinstance(node.iter, ast.Attribute) and node.iter.attr == 'deltas'):
            node.body = body
            return node
        obj = self.namespace[node.iter.value.id]
        deltas = obj.deltas
        unique_weights = list({i for i in obj.weights.flatten() if i})
        print("unique weights:", unique_weights)

        sym = SymbolRef(node.target.id)
        output = MultiNode([
            SymbolRef(sym.name, sym_type=ctypes.c_uint64())
        ])

        for delta in deltas:
            weight = Number(obj.weights[delta], ctype=ctypes.c_int64)
            renamer = DeltaRenamer(sym.name, weight)
            symbol_replacer = SymbolReplacer(sym.name, Number(encode(delta, ctype=ctypes.c_uint64), ctype=ctypes.c_uint64))
            body_copy = MultiNode(body=copy.deepcopy(body))
            body_copy = renamer.visit(body_copy)
            body_copy = symbol_replacer.visit(body_copy)
            output.body.append(body_copy)
        return output
