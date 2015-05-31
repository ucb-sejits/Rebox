from specializers.order import FunctionGenerator

__author__ = 'nzhang-dev'

class Add(FunctionGenerator):
    name = 'add'
    def __call__(self, index1, index2):
        return index1 + index2