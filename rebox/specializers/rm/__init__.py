import ast
import ctypes

from ctree.c.nodes import Assign, SymbolRef, ArrayDef, MultiNode, For, Lt, Number, PostInc, Array, Add, Mul

from rebox.specializers.generic import EncodeConvertTransformer


__author__ = 'nzhang-dev'

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