__author__ = 'nzhang-dev'

from ctree.c.nodes import CFile, MultiNode
from ctree.cpp.nodes import CppInclude
from collections import namedtuple

import abc

class OrderGenerator(object):
    __metaclass__ = abc.ABCMeta

    GeneratedResult = namedtuple("GeneratedResult", ["func", "auxiliary"])

    def generate_block(self, ndim, bits_per_dim, ctype, prefix=''):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits in each dimension
        :param ctype: ctype of index
        :return: MultiNode consisting of encode, add, and clamp
        """
        master = MultiNode()
        decls = []
        auxes = []
        for meth, name in zip((self.generate_add, self.generate_clamp, self.generate_encode), ("add", "clamp", "encode")):
            decl, aux = meth(ndim, bits_per_dim, ctype, prefix + name)
            decls.append(decl)
            auxes.extend(aux)

        includes = [
            CppInclude(target) for target in ("stdint.h", )
        ]


        master.body = includes + auxes + decls
        return master

    @abc.abstractmethod
    def generate_encode(self, ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: GeneratedResult with everything required, including FunctionDecl void <name> (param1, param2...) -> Z order index
        """


    @abc.abstractmethod
    def generate_add(self, ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: GeneratedResult with everything required, including FunctionDecl void <name> (*ctype param1, param2)
        """

    @abc.abstractmethod
    def generate_clamp(self, ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: GeneratedResult with everything required, including FunctionDecl void <name> (*ctype param) -> In place clamp
        """

