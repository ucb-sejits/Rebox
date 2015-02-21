__author__ = 'nzhang-dev'


import math
import itertools
import abc


def to_base(num, base):
    total = []
    while num:
        num, output = divmod(num, base)
        total.append(output)
    return reversed(total)

class Ordering(object):

    __metaclass__ = abc.ABCMeta

    @property
    def index(self):
        return self._index

    @abc.abstractmethod
    def __init__(self, indices, dimensions):
        pass

    @abc.abstractmethod
    def __add__(self, other):
        pass

    @abc.abstractmethod
    def __sub__(self, other):
        pass

    @abc.abstractmethod
    def __mul__(self, other):
        pass

    @abc.abstractmethod
    def __div__(self, other):
        pass

    @abc.abstractmethod
    def __truediv__(self, other):
        pass


class ZOrder(Ordering):

    def __init__(self, indices, dimensions):
        output = 0
        self.stride = len(indices)
        num_bits = int(math.ceil(max(math.log(index, 2) for index in indices))) + 1
        for mask in range(0, num_bits):
            for shift, index in enumerate(indices):
                output |= (index & (1 << mask)) << shift
        self._index = output

    def __add__(self, other):
        """
        other must be a tuple indicating deltas in each direction
        """


def z_order(indices, dimensions):
    """
    :param indices: Indices
    :param dimensions: Doesn't really matter, since z-index is dimension-agnostic
    :return: linearized index, using shift-mask method
    """
    output = 0
    length = len(indices)
    num_bits = int(math.ceil(max(math.log(index, 2) for index in indices))) + 1
    for mask in range(0, num_bits):
        for shift, index in enumerate(indices):
            output |= (index & (1 << mask)) << shift
    return output

def regular_order(indices, dimensions):
    """
    :param indices: tuple of sought index
    :param dimensions: length of each dimension
    :return: linearized index, using successive multiply method
    """
    thickness = 1
    output = 0
    for index, depth in reversed(zip(indices, dimensions)):
        output += index * thickness
        thickness *= depth
    return output
