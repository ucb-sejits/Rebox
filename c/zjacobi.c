

static const uint32_t repeat_mask_array[2] = {0x55555555, 0xaaaaaaaa};
static inline uint32_t add(uint32_t code, uint32_t code2) {
    uint32_t output = 0;
    uint32_t masked_code;
    uint32_t masked_code2;
    masked_code = code | ~ repeat_mask_array[0x0];
    masked_code2 = code2 & repeat_mask_array[0x0];
    output |= masked_code + masked_code2 & repeat_mask_array[0x0];
    masked_code = code | ~ repeat_mask_array[0x1];
    masked_code2 = code2 & repeat_mask_array[0x1];
    output |= masked_code + masked_code2 & repeat_mask_array[0x1];
    return output;
};


static const uint32_t underflow_mask[4] = {0x0, 0x55555555, 0xaaaaaaaa, 0xffffffff};
static const uint32_t overflow_mask[4] = {0x0, 0x15555, 0x2aaaa, 0x3ffff};
static inline void clamp(uint32_t* code) {
    * code &= ~ underflow_mask[(* code >> 0x12 & 0x3)];
    uint32_t mask = * code >> 0x12 & 0xfff;
    * code |= overflow_mask[((mask >> 0x0 | mask >> 0x2 | mask >> 0x4 | mask >> 0x6 | mask >> 0x8 | mask >> 0xa) & 0x3)];
    * code &= 0x3ffff;
};


static const uint32_t lookup_table[0x2][256] = {{0x0, 0x1, 0x4, 0x5, 0x10, 0x11, 0x14, 0x15, 0x40, 0x41, 0x44, 0x45, 0x50, 0x51, 0x54, 0x55, 0x100, 0x101, 0x104, 0x105, 0x110, 0x111, 0x114, 0x115, 0x140, 0x141, 0x144, 0x145, 0x150, 0x151, 0x154, 0x155, 0x400, 0x401, 0x404, 0x405, 0x410, 0x411, 0x414, 0x415, 0x440, 0x441, 0x444, 0x445, 0x450, 0x451, 0x454, 0x455, 0x500, 0x501, 0x504, 0x505, 0x510, 0x511, 0x514, 0x515, 0x540, 0x541, 0x544, 0x545, 0x550, 0x551, 0x554, 0x555, 0x1000, 0x1001, 0x1004, 0x1005, 0x1010, 0x1011, 0x1014, 0x1015, 0x1040, 0x1041, 0x1044, 0x1045, 0x1050, 0x1051, 0x1054, 0x1055, 0x1100, 0x1101, 0x1104, 0x1105, 0x1110, 0x1111, 0x1114, 0x1115, 0x1140, 0x1141, 0x1144, 0x1145, 0x1150, 0x1151, 0x1154, 0x1155, 0x1400, 0x1401, 0x1404, 0x1405, 0x1410, 0x1411, 0x1414, 0x1415, 0x1440, 0x1441, 0x1444, 0x1445, 0x1450, 0x1451, 0x1454, 0x1455, 0x1500, 0x1501, 0x1504, 0x1505, 0x1510, 0x1511, 0x1514, 0x1515, 0x1540, 0x1541, 0x1544, 0x1545, 0x1550, 0x1551, 0x1554, 0x1555, 0x4000, 0x4001, 0x4004, 0x4005, 0x4010, 0x4011, 0x4014, 0x4015, 0x4040, 0x4041, 0x4044, 0x4045, 0x4050, 0x4051, 0x4054, 0x4055, 0x4100, 0x4101, 0x4104, 0x4105, 0x4110, 0x4111, 0x4114, 0x4115, 0x4140, 0x4141, 0x4144, 0x4145, 0x4150, 0x4151, 0x4154, 0x4155, 0x4400, 0x4401, 0x4404, 0x4405, 0x4410, 0x4411, 0x4414, 0x4415, 0x4440, 0x4441, 0x4444, 0x4445, 0x4450, 0x4451, 0x4454, 0x4455, 0x4500, 0x4501, 0x4504, 0x4505, 0x4510, 0x4511, 0x4514, 0x4515, 0x4540, 0x4541, 0x4544, 0x4545, 0x4550, 0x4551, 0x4554, 0x4555, 0x5000, 0x5001, 0x5004, 0x5005, 0x5010, 0x5011, 0x5014, 0x5015, 0x5040, 0x5041, 0x5044, 0x5045, 0x5050, 0x5051, 0x5054, 0x5055, 0x5100, 0x5101, 0x5104, 0x5105, 0x5110, 0x5111, 0x5114, 0x5115, 0x5140, 0x5141, 0x5144, 0x5145, 0x5150, 0x5151, 0x5154, 0x5155, 0x5400, 0x5401, 0x5404, 0x5405, 0x5410, 0x5411, 0x5414, 0x5415, 0x5440, 0x5441, 0x5444, 0x5445, 0x5450, 0x5451, 0x5454, 0x5455, 0x5500, 0x5501, 0x5504, 0x5505, 0x5510, 0x5511, 0x5514, 0x5515, 0x5540, 0x5541, 0x5544, 0x5545, 0x5550, 0x5551, 0x5554, 0x5555}, {0x0, 0x2, 0x8, 0xa, 0x20, 0x22, 0x28, 0x2a, 0x80, 0x82, 0x88, 0x8a, 0xa0, 0xa2, 0xa8, 0xaa, 0x200, 0x202, 0x208, 0x20a, 0x220, 0x222, 0x228, 0x22a, 0x280, 0x282, 0x288, 0x28a, 0x2a0, 0x2a2, 0x2a8, 0x2aa, 0x800, 0x802, 0x808, 0x80a, 0x820, 0x822, 0x828, 0x82a, 0x880, 0x882, 0x888, 0x88a, 0x8a0, 0x8a2, 0x8a8, 0x8aa, 0xa00, 0xa02, 0xa08, 0xa0a, 0xa20, 0xa22, 0xa28, 0xa2a, 0xa80, 0xa82, 0xa88, 0xa8a, 0xaa0, 0xaa2, 0xaa8, 0xaaa, 0x2000, 0x2002, 0x2008, 0x200a, 0x2020, 0x2022, 0x2028, 0x202a, 0x2080, 0x2082, 0x2088, 0x208a, 0x20a0, 0x20a2, 0x20a8, 0x20aa, 0x2200, 0x2202, 0x2208, 0x220a, 0x2220, 0x2222, 0x2228, 0x222a, 0x2280, 0x2282, 0x2288, 0x228a, 0x22a0, 0x22a2, 0x22a8, 0x22aa, 0x2800, 0x2802, 0x2808, 0x280a, 0x2820, 0x2822, 0x2828, 0x282a, 0x2880, 0x2882, 0x2888, 0x288a, 0x28a0, 0x28a2, 0x28a8, 0x28aa, 0x2a00, 0x2a02, 0x2a08, 0x2a0a, 0x2a20, 0x2a22, 0x2a28, 0x2a2a, 0x2a80, 0x2a82, 0x2a88, 0x2a8a, 0x2aa0, 0x2aa2, 0x2aa8, 0x2aaa, 0x8000, 0x8002, 0x8008, 0x800a, 0x8020, 0x8022, 0x8028, 0x802a, 0x8080, 0x8082, 0x8088, 0x808a, 0x80a0, 0x80a2, 0x80a8, 0x80aa, 0x8200, 0x8202, 0x8208, 0x820a, 0x8220, 0x8222, 0x8228, 0x822a, 0x8280, 0x8282, 0x8288, 0x828a, 0x82a0, 0x82a2, 0x82a8, 0x82aa, 0x8800, 0x8802, 0x8808, 0x880a, 0x8820, 0x8822, 0x8828, 0x882a, 0x8880, 0x8882, 0x8888, 0x888a, 0x88a0, 0x88a2, 0x88a8, 0x88aa, 0x8a00, 0x8a02, 0x8a08, 0x8a0a, 0x8a20, 0x8a22, 0x8a28, 0x8a2a, 0x8a80, 0x8a82, 0x8a88, 0x8a8a, 0x8aa0, 0x8aa2, 0x8aa8, 0x8aaa, 0xa000, 0xa002, 0xa008, 0xa00a, 0xa020, 0xa022, 0xa028, 0xa02a, 0xa080, 0xa082, 0xa088, 0xa08a, 0xa0a0, 0xa0a2, 0xa0a8, 0xa0aa, 0xa200, 0xa202, 0xa208, 0xa20a, 0xa220, 0xa222, 0xa228, 0xa22a, 0xa280, 0xa282, 0xa288, 0xa28a, 0xa2a0, 0xa2a2, 0xa2a8, 0xa2aa, 0xa800, 0xa802, 0xa808, 0xa80a, 0xa820, 0xa822, 0xa828, 0xa82a, 0xa880, 0xa882, 0xa888, 0xa88a, 0xa8a0, 0xa8a2, 0xa8a8, 0xa8aa, 0xaa00, 0xaa02, 0xaa08, 0xaa0a, 0xaa20, 0xaa22, 0xaa28, 0xaa2a, 0xaa80, 0xaa82, 0xaa88, 0xaa8a, 0xaaa0, 0xaaa2, 0xaaa8, 0xaaaa}};
static inline uint32_t encode(uint32_t* indices) {
    return (lookup_table[0x0][(indices[0x0] >> 0x0 & 0xff)] | lookup_table[0x1][(indices[0x1] >> 0x0 & 0xff)]) << 0x0 | (lookup_table[0x0][(indices[0x0] >> 0x8 & 0xff)] | lookup_table[0x1][(indices[0x1] >> 0x8 & 0xff)]) << 0x8;
};


