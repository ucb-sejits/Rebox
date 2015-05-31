from collections import namedtuple
import ctypes
import time

from ctree.jit import LazySpecializedFunction, ConcreteSpecializedFunction
from ctree.nodes import Project
import numpy as np

from specializers.generic.util import indices, add


__author__ = 'nzhang-dev'

class StencilFunction(ConcreteSpecializedFunction):

    def finalize(self, entry_point_name, project_node, entry_point_typesig):
        self._c_function = self._compile(entry_point_name, project_node, entry_point_typesig)
        return self

    def __call__(self, arr, out=None):
        t = time.time()
        if out is None:
            out = np.ndarray(arr.shape, arr.dtype)
        t2 = time.time()
        flattened = [arr.ravel(), out.ravel()]
        t3 = time.time()
        self._c_function(*flattened)
        t4 = time.time()
        print("Out allocation", t2-t, "Flatten", t3-t2, "Calculation", t4-t3)
        return out


class Stencil(LazySpecializedFunction):
    _weights = np.ones((1,1,1))  # identity stencil
    _out = None

    Subconfig = namedtuple("Subconfig", ["dtype", "ndim", "shape"])

    def __init__(self, in_code, out_code, boundary_handler):
        super(self, Stencil).__init__()
        self.in_code = in_code
        self.out_code = out_code
        self.boundary_handler = boundary_handler

    def args_to_subconfig(self, args):
        A = args[0]
        return self.Subconfig(A.dtype, A.ndim, A.shape)

    def transform(self, tree, program_config):
        pass

    def finalize(self, transform_result, program_config):
        proj = Project(transform_result)
        subconfig = program_config.args_subconfig
        argtype = np.ctypeslib.ndpointer(subconfig.dtype, 1, np.multiply.reduce(subconfig.shape))
        fn = StencilFunction()
        return fn.finalize("apply", proj, ctypes.CFUNCTYPE(None, argtype, argtype))

    @property
    def deltas(self):
        for index in zip(*self._weights.nonzero()):
            yield tuple(ind - (diameter - 1)/2 for ind, diameter in zip(index, self._weights.shape))

    @property
    def weights(self):
        if self._out is not None:
            return self._out
        out = np.zeros_like(self._weights)
        for delta, index in zip(self.deltas, zip(*self._weights.nonzero())):
            out[tuple(delta)] = self._weights[tuple(index)]
        self._out = out
        return self._out

    def apply(self, arr, out):
        for index in indices(arr):
            total = 0
            for delta in self.deltas:
                total += arr[self.boundary_handler(add(index, delta))] * self.weights[delta]
            out[self.encode(index)] = total
        return out