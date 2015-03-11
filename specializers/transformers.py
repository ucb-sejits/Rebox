__author__ = 'nzhang-dev'
import ast
import ctree.c.nodes

class PreReturnInsertionTransformer(ast.NodeTransformer):
    """
    Inserts nodes in before Return.
    """

    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def visit_Return(self, node):
        body = self.nodes + [node]
        return ctree.c.nodes.MultiNode(body=body)
