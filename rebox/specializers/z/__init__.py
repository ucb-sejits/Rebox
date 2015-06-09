from rebox.specializers.z.add import FastBitMagicAdd
from rebox.specializers.z.clamp import PartialMulClamp
from rebox.specializers.z.decode import LUTShiftDecode
from rebox.specializers.z.encode import SLUTEncode

generators = {
    'clamp': PartialMulClamp,
    'add': FastBitMagicAdd,
    'encode': SLUTEncode,
    'decode': LUTShiftDecode
}