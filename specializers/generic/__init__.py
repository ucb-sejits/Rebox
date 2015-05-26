import ast
from ctree.c.nodes import Number, SymbolRef, Op, MultiNode

__author__ = 'nzhang-dev'


class ClampSimplifier(ast.NodeTransformer):
    """
    Don't have to clamp if you're operating on a known valid expression
    """
    def visit_FunctionCall(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        if node.func.name == 'clamp':
            if isinstance(node.args[0], (Number, SymbolRef)):
                return node.args[0]
        return node

class MulSimplifier(ast.NodeTransformer):
    """
    x*0 = 0, x*1 = x
    """
    def visit_BinaryOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        if isinstance(node.op, Op.Mul):
            for cur, opposite in ((node.left, node.right), (node.right, node.left)):
                if isinstance(cur, Number):
                    if cur.value == 1:
                        return opposite
                    if cur.value == 0:
                        return Number(0)
            return node
        return node


class SymbolReplacer(ast.NodeTransformer):
    def __init__(self, target, replacement):
        self.target = target
        self.replacement = replacement

    def visit_SymbolRef(self, node):
        if node.name == self.target:
            return self.replacement
        return node

class CleanArgsTransformer(ast.NodeTransformer):
    def visit_FunctionCall(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        if node.func.name != 'clamp' or len(node.args) == 1:
            return node
        node.args = [node.args[0]]
        return node

class ReturnRemover(ast.NodeTransformer):
    def visit_Return(self, node):
        return None


class CompoundTransformer(ast.NodeTransformer):
    def __init__(self, transformers):
        self.transformers = transformers

    def visit(self, node):
        for transformer in self.transformers:
            node = transformer.visit(node)
        return node

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

class AddSimplifier(ast.NodeTransformer):
    def visit_BinaryOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        if isinstance(node.op, Op.Add):
            for cur, opposite in ((node.left, node.right), (node.right, node.left)):
                if isinstance(cur, Number) and cur.value == 0:
                    return opposite
            return node
        return node

    def visit_FunctionCall(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        if node.func.name == 'add':
            for cur, opposite in (node.args, node.args[::-1]):
                if isinstance(cur, Number) and cur.value == 0:
                    return opposite
            return node
        return node

class PreReturnInsertionTransformer(ast.NodeTransformer):
    """
    Inserts nodes in before Return.
    """

    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def visit_Return(self, node):
        body = self.nodes + [node]
        return MultiNode(body=body)

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