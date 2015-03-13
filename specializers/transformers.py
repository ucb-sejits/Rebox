__author__ = 'nzhang-dev'
import ast
import ctypes

from ctree.frontend import dump

from functools import reduce

import itertools

from ctree.c.nodes import (MultiNode, For, SymbolRef, Assign, Constant, ArrayDef, PostInc, Array, Lt, String, Op,
                            Mul, Add)

class PreReturnInsertionTransformer(ast.NodeTransformer):
    """
    Inserts nodes in before Return.
    """

    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def visit_Return(self, node):
        body = self.nodes + [node]
        return MultiNode(body=body)


class IndexTransformer(ast.NodeTransformer):
    def __init__(self, namespace, ctype=ctypes.c_uint):
        super(ast.NodeTransformer, self).__init__()
        self.namespace = namespace
        self.ctype = ctype
        self.count = 0

    def visit_For(self, node):
        if not (isinstance(node.iter, ast.Call) and node.iter.func.id == "_indices"):
            return node
        shapes = self.namespace[node.iter.args[0].id].shape
        new_count = self.count + len(shapes)
        variables = ["__{}".format(i) for i in range(self.count, new_count)]
        self.count = new_count
        symbols = [SymbolRef(s) for s in variables]
        initializers = (
            Assign(SymbolRef(var, sym_type=self.ctype()), Constant(0)) for var in variables
        )
        target = SymbolRef(node.target.id, sym_type=self.ctype())

        target_assign = ArrayDef(target=target, size=len(shapes), body=Array(body=symbols))

        body = MultiNode(body=[target_assign]+[self.visit(i) for i in node.body])  # make a copy

        top = body
        for shape, initializer, symbol in reversed(zip(shapes, initializers, symbols)):
            top = For(initializer, Lt(symbol, Constant(shape)), PostInc(symbol), body=[top])

        def replacement(node):
            """
            :param node: node with a matched name
            :return: new node that is properly encoded
            """
            reversed_dims = reversed(shapes)
            indices = iter(symbols)
            out = next(indices)
            for var in indices:
                out = Add(Mul(out, Constant(next(reversed_dims))), var)
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

