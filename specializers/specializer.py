__author__ = 'nzhang-dev'

from ctree.c.nodes import CFile, MultiNode

import abc

class OrderGenerator(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def generate_block(cls, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits in each dimension
        :param ctype: ctype of index
        :return: MultiNode consisting of encode, add, and clamp
        """
        master = MultiNode()
        for meth, name in zip((cls.generate_add, cls.generate_clamp, cls.generate_encode), ("add", "clamp", "encode")):
            master.body.append(
                meth(ndim, bits_per_dim, ctype, name)
            )

        return master

    @staticmethod
    @abc.abstractmethod
    def generate_encode(ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (param1, param2...) -> Z order index
        """

    @staticmethod
    @abc.abstractmethod
    def generate_add(ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype param1, param2)
        """

    @staticmethod
    @abc.abstractmethod
    def generate_clamp(ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: bits per dimension
        :param ctype: ctype of data
        :param name: name of function
        :return: MultiNode with everything required, including FunctionDecl void <name> (*ctype param) -> In place clamp
        """

