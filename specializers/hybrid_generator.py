__author__ = 'nzhang-dev'

from ctree.c.nodes import MultiNode

from order import OrderGenerator

class HybridOrder(OrderGenerator):
    """
    Class for generation of hybrid orderings (z ordering for high order bits, row-major for lower order).

    For example, a 3-D (x, y, z) 2-bit Z (per dimension) with 4 bit (per dimension) standard ordering would look like this:

    ZYX ZYX ZZZZ YYYY XXXX
    """

    def __init__(self, generators):
        """
        :param generators: takes an iterable of generators as setup
        """
        self._generators = tuple(generators)


    def generate_add(self, ndim, bits_per_dim, ctype):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: Tuple (bits/dim for each ordering)
        :param ctype: ctype of arguments
        :param name: name of function
        :return: CNode with relevant code
        """
        bits_per_dim += [0]*(len(self._generators) - len(bits_per_dim))
        master = MultiNode(
            [generator.generate_add(bits) for generator, bits in zip(self._generators, bits_per_dim)]
        )

        return master


    def generate_clamp(self, ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: Tuple (Z bits (high order), Row-Major (lower order))
        :param ctype: ctype of arguments
        :param name: name of function
        :return: CNode with relevant code
        """
        bits_per_dim += [0]*(len(self._generators) - len(bits_per_dim))
        master = MultiNode(
            [generator.generate_clamp(bits) for generator, bits in zip(self._generators, bits_per_dim)]
        )

        return master

    def generate_encode(self, ndim, bits_per_dim, ctype, name):
        """
        :param ndim: number of dimensions
        :param bits_per_dim: Tuple (Z bits (high order), Row-Major (lower order))
        :param ctype: ctype of arguments
        :param name: name of function
        :return: CNode with relevant code
        """

        bits_per_dim += [0]*(len(self._generators) - len(bits_per_dim))
        master = MultiNode(
            [generator.generate_encode(bits) for generator, bits in zip(self._generators, bits_per_dim)]
        )

        return master
