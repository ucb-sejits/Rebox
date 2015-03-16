__author__ = 'nzhang-dev'
import simple_stencil
from specializers.zorder import EncodeConversion

class ZStencil(simple_stencil.SimpleStencil):
    _reordered = False
    boundary_type = 'clamp'

    def __init__(self):
        super(ZStencil, self).__init__()
        if not self._reordered:
            self._reordered = True
            self.weights = EncodeConversion.apply(self.weights)