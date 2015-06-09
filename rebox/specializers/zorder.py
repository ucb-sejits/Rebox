from __future__ import division, print_function

__author__ = 'nzhang-dev'

import math
import numpy as np
import ctypes
from collections import namedtuple
import ast

from ctree.jit import LazySpecializedFunction, ConcreteSpecializedFunction
from ctree.cpp.nodes import CppInclude
from ctree.c.nodes import CFile, SymbolRef
from ctree.nodes import Project
from transformers import IndexTransformer
from ctree.transformations import PyBasicConversions

from order import Ordering
from rebox.specializers.z.z_generator import Encode


from rebox.specializers.generic.util import encode, indices

class ZFunction(ConcreteSpecializedFunction):

    def finalize(self, entry_point_name, project_node, entry_point_typesig):
        self._c_function = self._compile(entry_point_name, project_node, entry_point_typesig)
        return self

    def __call__(self, arr, output=None):
        if output is None:
            output = np.ndarray(shape=arr.shape, dtype=arr.dtype)
        self._c_function(arr.flatten(), output.flatten())
        return output




class EncodeConversion(LazySpecializedFunction):
    Subconfig = namedtuple("Subconfig", ["dtype", "ndim", "shape"])

    def args_to_subconfig(self, args):
        A = args[0]
        return self.Subconfig(A.dtype, A.ndim, A.shape)

    def transform(self, tree, program_config):
        """
        :param tree: apply's tree
        :param program_config: only really want the subconfig
        :return: iterable of Files
        """

        # encode for indexing
        generator = generator = Ordering([Encode()])
        subconfig = program_config.args_subconfig
        max_dim = max(subconfig.shape)
        bits_per_dim = int(math.ceil(math.log(max_dim, 2)))
        types = (ctypes.c_uint32, ctypes.c_uint64)
        smallest_enclosing_type = [i for i in types if ctypes.sizeof(i)*8 >= bits_per_dim + 2*subconfig.ndim][0]
        block = generator.generate(subconfig.ndim, bits_per_dim, smallest_enclosing_type)

        tree = tree.body[0]
        tree.body = [i for i in tree.body if isinstance(i, ast.For)]  # the For loop is all we actually need

        # muxing around with apply's ast
        c_ast = PyBasicConversions().visit(tree)
        index_visitor = IndexTransformer({tree.args.args[0].id: subconfig, "out": subconfig})
        c_ast = index_visitor.visit(c_ast)
        param_type = np.ctypeslib.ndpointer(subconfig.dtype, 1, np.multiply.reduce(subconfig.shape))
        c_ast.params.append(SymbolRef("out"))
        for param in c_ast.params:
            param.type = param_type()
        includes = [
            CppInclude("auxiliary.c",angled_brackets=False)
        ]

        main = CFile(name="main", body=includes+[c_ast])
        #print(main)
        aux = CFile(name="auxiliary", body=[block])
        #print(aux)
        return aux, main

    def finalize(self, transform_result, program_config):
        proj = Project(transform_result)
        subconfig = program_config.args_subconfig
        argtype = np.ctypeslib.ndpointer(subconfig.dtype, 1, np.multiply.reduce(subconfig.shape))
        fn = ZFunction()
        return fn.finalize("apply", proj, ctypes.CFUNCTYPE(None, argtype, argtype))


    @staticmethod
    def apply(in_arr):
        out = np.zeros_like(in_arr).flatten()
        for index in indices(in_arr):
            out[encode(index)] = in_arr[index]
        return out

class DecodeConversion(EncodeConversion):
    @staticmethod
    def apply(in_arr):
        out = np.zeros((8,8))
        for index in indices(out):
            out[index] = in_arr[encode(index)]
        return out


if __name__ == "__main__":
    arr = np.arange(64).reshape((8, 8))
    print(arr)
    encoder = EncodeConversion()
    encoded = encoder(arr)
    decoder = DecodeConversion()
    other_encoded = encoder.apply(arr)
    decoded = decoder.apply(encoded)
    print(encoded)
    print(decoded)
