__author__ = 'nzhang-dev'

from ctree.jit import LazySpecializedFunction, ConcreteSpecializedFunction
import numpy as np
import itertools

class SimpleStencil(LazySpecializedFunction):
    weights = np.array([])
    boundary_type = 'clamp'

    def embed(self, arr, target):
        slices = [slice((diameter - 1)/2, -(diameter - 1)/2) for diameter in self.weights.shape]
        target[slices] = arr
        return target

    def apply_boundary_conditions(self, arr):
        target_shape = [dim + diameter - 1 for dim, diameter in zip(arr.shape, self.weights.shape)]
        target = np.zeros(target_shape, dtype=arr.dtype)

        if self.boundary_type == 'wrap':
            raise NotImplemented("Wrap hasn't been put in yet")


        if self.boundary_type == 'clamp':
            self.embed(arr, target)
            min_indices = [(diameter - 1)/2 for diameter in self.weights.shape]
            max_indices = [dim - min_index - 1 for dim, min_index in zip(target.shape, min_indices)]
            for coord in itertools.product(*[range(dim) for dim in target.shape]):
                clamped = tuple(min(max(min_index, i), max_index) for min_index, max_index, i in
                           zip(min_indices, max_indices, coord))
                target[coord] = target[clamped]
        else:
            self.embed(arr, target)
        return target

    def apply(self, arr):
        embedded = self.apply_boundary_conditions(arr)
        radii = [(diameter - 1)/2 for diameter in self.weights.shape]
        out = np.zeros_like(arr)
        for index in itertools.product(*[range(dim) for dim in arr.shape]):
            adjusted_index = [radius + i for radius, i in zip(radii, index)]
            neighborhood_slice = tuple(slice(i - radius, i + radius + 1) for i, radius in zip(adjusted_index, radii))
            out[index] = np.dot(self.weights.flatten(), embedded[neighborhood_slice].flatten())
        return out

class SumStencil(SimpleStencil):
    weights = np.ones((3, 3, 3), dtype=np.float32)
    boundary_type = 'clamp'

if __name__ == "__main__":
    #np.set_printoptions(threshold='nan')
    arr = np.ones((128,)*3, dtype=np.float)
    sum2 = SumStencil()
    print(sum2.apply(arr))