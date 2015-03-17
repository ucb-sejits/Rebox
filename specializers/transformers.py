__author__ = 'nzhang-dev'
import ast
import ctypes
import copy
import numpy as np

from ctree.frontend import dump

from functools import reduce

import itertools

from ctree.c.nodes import (MultiNode, For, SymbolRef, Assign, Number, ArrayDef, PostInc, Array, Lt, String, Op,
                            Mul, Add, BinaryOp)

from util import encode

class PreReturnInsertionTransformer(ast.NodeTransformer):
    """
    Inserts nodes in before Return.
    """

    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def visit_Return(self, node):
        body = self.nodes + [node]
        return MultiNode(body=body)

class ZIndexTransformer(ast.NodeTransformer):
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

class IndexTransformer(ast.NodeTransformer):
    def __init__(self, namespace, ctype=ctypes.c_uint):
        super(ast.NodeTransformer, self).__init__()
        self.namespace = namespace
        self.ctype = ctype
        self.count = 0

    def visit_For(self, node):
        body = [self.visit(i) for i in node.body]
        if not (isinstance(node, ast.For) and isinstance(node.iter, ast.Call) and node.iter.func.id == "indices"):
            node.body = body
            return node
        shapes = self.namespace[node.iter.args[0].id].shape
        new_count = self.count + len(shapes)
        variables = ["__{}".format(i) for i in range(self.count, new_count)]
        self.count = new_count
        symbols = [SymbolRef(s) for s in variables]
        initializers = (
            Assign(SymbolRef(var, sym_type=self.ctype()), Number(0)) for var in variables
        )
        target = SymbolRef(node.target.id, sym_type=self.ctype())

        target_assign = ArrayDef(target=target, size=len(shapes), body=Array(body=symbols))

        body = MultiNode(body=[target_assign]+[self.visit(i) for i in node.body])  # make a copy

        top = body
        for shape, initializer, symbol in reversed(zip(shapes, initializers, symbols)):
            top = For(initializer, Lt(symbol, Number(shape)), PostInc(symbol), body=[top])

        def replacement(node):
            """
            :param node: node with a matched name
            :return: new node that is properly encoded
            """
            reversed_dims = reversed(shapes)
            indices = iter(symbols)
            out = next(indices)
            for var in indices:
                out = Add(Mul(out, Number(next(reversed_dims))), var)
            return out

        top = EncodeConvertTransformer("index", replacement).visit(top)
        return top

class EncodeConvertTransformer(ast.NodeTransformer):
    def __init__(self, target, replacement_func):
        self.target = target
        self.replacement_func = replacement_func

    def visit_BinaryOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        if isinstance(node.op, Op.ArrayRef) and isinstance(node.right, SymbolRef):
            node.right = self.replacement_func(node.right)
        return node

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

        sym = SymbolRef(node.target.id)
        output = MultiNode([
            SymbolRef(sym.name, sym_type=ctypes.c_uint64())
        ])
        for delta in deltas:
            weight = Number(obj.weights[delta], ctype=ctypes.c_int64)
            renamer = DeltaRenamer(sym.name, weight)
            output.body.append(Assign(sym, Number(encode(delta, ctype=ctypes.c_uint64), ctype=ctypes.c_uint64)))
            body_copy = MultiNode(body=copy.deepcopy(body))
            body_copy = renamer.visit(body_copy)
            output.body.append(body_copy)
        return output

class DeltaRenamer(ast.NodeTransformer):
    def __init__(self, name, target):
        self.name = name  # renames self.weight[name] to target
        self.target = target  #renames to target

    def visit_BinaryOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        if not isinstance(node.op, Op.ArrayRef):
            return node
        try:
            if not node.left.value.name == 'self' and node.left.attr == 'weights' and node.right.name == self.name:
                return node
            return self.target
        except AttributeError:
            pass
        return node

class CleanArgsTransformer(ast.NodeTransformer):
    def visit_FunctionCall(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        if node.func.name != 'clamp' or len(node.args) == 1:
            return node
        node.args = [node.args[0]]
        return node


class CompoundTransformer(ast.NodeTransformer):
    def __init__(self, transformers):
        self.transformers = transformers

    def visit(self, node):
        for transformer in self.transformers:
            node = transformer.visit(node)
        return node




