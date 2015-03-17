__author__ = 'nzhang-dev'
import itertools
import numpy as np
from collections import namedtuple
import ctypes
import math

from ctree.jit import LazySpecializedFunction, ConcreteSpecializedFunction
from ctree.c.nodes import CFile, For
from ctree.nodes import Project
from ctree.cpp.nodes import CppInclude
from ctree.transformations import PyBasicConversions
from ctree.transforms.declaration_filler import DeclarationFiller
from ctree.tune import BruteForceTuningDriver, EnumParameter, MinimizeTime

from specializers.transformers import DeltaTransformer, CleanArgsTransformer, ZIndexTransformer
from specializers import z_generator
from specializers.util import indices, add, clamp

from specializers.zorder import EncodeConversion, DecodeConversion

import time

class ZStencilFunction(ConcreteSpecializedFunction):

    def finalize(self, entry_point_name, project_node, entry_point_typesig):
        self._c_function = self._compile(entry_point_name, project_node, entry_point_typesig)
        return self

    def __call__(self, arr):
        output = np.zeros_like(arr.flatten())
        self._c_function(arr.flatten(), output)
        return output.reshape(arr.shape)

class ZStencil(LazySpecializedFunction):
    _weights = np.ones((1,1,1))  # identity stencil
    _out = None

    Subconfig = namedtuple("Subconfig", ["dtype", "ndim", "shape"])

    def get_tuning_driver(self):
        add_param = EnumParameter("add", [z_generator.Add2, z_generator.Add3, z_generator.Add4])
        clamp_param = EnumParameter("clamp", [z_generator.LUTClamp, z_generator.MulClamp, z_generator.PartialMulClamp])
        driver = BruteForceTuningDriver(params=[add_param, clamp_param], objective=MinimizeTime())
        return driver

    def args_to_subconfig(self, args):
        A = args[0]
        return self.Subconfig(A.dtype, A.ndim, A.shape)

    def transform(self, tree, program_config):
        print(program_config)
        aux_functions = [init() for init in program_config.tuner_subconfig.values()]
        auxiliary_codegen = z_generator.Ordering(aux_functions)
        subconfig = program_config.args_subconfig
        max_dim = max(subconfig.shape)
        bits_per_dim = int(math.ceil(math.log(max_dim, 2)))

        aux_file = CFile(name="aux", body=auxiliary_codegen.generate(subconfig.ndim, bits_per_dim, ctypes.c_uint64))

        tree = tree.body[0]
        tree.args.args.pop(0)  # remove self
        tree.body.pop(0)  # removes initialization of out
        c_tree = PyBasicConversions().visit(tree)
        c_tree = CleanArgsTransformer().visit(c_tree)
        c_tree = ZIndexTransformer({"arr":arr}, ctype=ctypes.c_uint64).visit(c_tree)
        c_tree = DeltaTransformer({"self": self}, ndim=len(subconfig.shape)).visit(c_tree)
        c_tree.defn.pop()
        includes = [
            CppInclude("stdint.h"),
            CppInclude("aux.c", angled_brackets=False)
        ]
        param_type = np.ctypeslib.ndpointer(subconfig.dtype, 1, np.multiply.reduce(subconfig.shape))
        for param in c_tree.params:
            param.type = param_type()
        main_file = CFile(body = includes + [c_tree])
        return [aux_file, main_file]

    def finalize(self, transform_result, program_config):
        proj = Project(transform_result)
        subconfig = program_config.args_subconfig
        argtype = np.ctypeslib.ndpointer(subconfig.dtype, 1, np.multiply.reduce(subconfig.shape))
        fn = ZStencilFunction()
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


    def apply(self, arr, out=None):
        out = np.zeros_like(arr) if out is None else out
        for index in indices(arr):
            total = 0
            for delta in self.deltas:
                total += arr[clamp(add(index, delta), arr.shape)] * self.weights[delta]
            out[index] = total
        return out

class ZOmpStencil(ZStencil):
    def transform(self, tree, program_config):
        files = super(ZOmpStencil, self).transform(tree, program_config)
        main_file = files[1]
        main_file.body.insert(0, CppInclude("omp.h"))
        loop = main_file.find(For)
        loop.pragma = "omp parallel for"
        return files

class BoxedZOmpStencil(ZStencil):
    def transform(self, tree, program_config):
        files = super(ZOmpStencil, self).transform(tree, program_config)
        main_file = files[1]
        main_file.body.insert(0, CppInclude("omp.h"))
        loop = main_file.find(For)
        loop.pragma = "omp parallel for"
        return files

class Laplacian2DStencil(ZStencil):
    _weights = np.array([
        [0, -1, 0],
        [-1, 4, -1],
        [0, -1, 0]
    ])

class Laplacian2DOmpStencil(Laplacian2DStencil, ZOmpStencil):
    pass

if __name__ == "__main__":
    ndim = 3
    shape = (1024,) * ndim
    arr = np.arange(shape[0]**ndim).reshape(shape)
    l2ds = Laplacian2DOmpStencil()
    encoder = EncodeConversion()
    decoder = DecodeConversion()
    encoded = encoder(arr)
    processed = l2ds(encoded.reshape(shape))
    decoded = decoder(processed)
    for i in range(9):
        print(i)
        t = time.time()
        decoder(l2ds(encoded.reshape(shape))).reshape(shape)
        end = time.time()
        l2ds.report(time=end - t)
        print(end - t)
    print(l2ds._tuner._best_cfg)