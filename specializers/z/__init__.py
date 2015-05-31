from specializers.z.add import FastBitMagicAdd
from specializers.z.clamp import PartialMulClamp
from specializers.z.decode import LUTShiftDecode
from specializers.z.encode import SLUTEncode

generators = {
    'clamp': PartialMulClamp,
    'add': FastBitMagicAdd,
    'encode': SLUTEncode,
    'decode': LUTShiftDecode
}