__author__ = 'nzhang-dev'

from ctree.c.nodes import CFile, MultiNode
from ctree.cpp.nodes import CppInclude
from collections import namedtuple

from functools import reduce
from operator import add

import abc

class FunctionGenerator(object):
    __metaclass__ = abc.ABCMeta

    GeneratedResult = namedtuple("GeneratedResult", ["func", "auxiliary", "includes"])
    GeneratedResult.__new__.__defaults__ = (None, (), ())
    name = ''


    @abc.abstractmethod
    def generate(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :return: GeneratedResult with everything required, including FunctionDecl void <name> (param1, param2...) -> Z order index
        """

class Ordering(object):
    default_includes = [CppInclude("stdint.h"), CppInclude("stdlib.h")]

    def __init__(self, generators=None, prefix='', suffix=''):
        self.generators = generators or []
        self.prefix = prefix
        self.suffix = suffix

    def generate(self, *params):
        generated = [generator.generate(*(params)) for generator in self.generators]
        decls, auxes, includes = zip(*generated)
        flattened_includes = self.default_includes[:]
        for include in includes:
            flattened_includes.extend(include)

        flattened_includes = list(set(flattened_includes))
        flattened_auxes = []
        for aux in auxes:
            flattened_auxes.extend(aux)
        for decl in decls:
            decl.name = self.prefix + decl.name + self.suffix
        return MultiNode(body = flattened_includes + flattened_auxes + list(decls))