

const size_t repeat_mask_array[3] = {0x9249249249249249L, 0x2492492492492492, 0x4924924924924924};
size_t add(size_t code, size_t code2) {
    size_t output = 0;
    size_t masked_code;
    size_t masked_code2;
    masked_code = code | ~ repeat_mask_array[0x0];
    masked_code2 = code2 & repeat_mask_array[0x0];
    output |= masked_code + masked_code2 & repeat_mask_array[0x0];
    masked_code = code | ~ repeat_mask_array[0x1];
    masked_code2 = code2 & repeat_mask_array[0x1];
    output |= masked_code + masked_code2 & repeat_mask_array[0x1];
    masked_code = code | ~ repeat_mask_array[0x2];
    masked_code2 = code2 & repeat_mask_array[0x2];
    output |= masked_code + masked_code2 & repeat_mask_array[0x2];
    return output;
};


const size_t underflow_mask[8] = {0x0, 0x9249249249249249L, 0x2492492492492492, 0xb6db6db6db6db6dbL, 0x4924924924924924, 0xdb6db6db6db6db6dL, 0x6db6db6db6db6db6, 0xffffffffffffffffL};
const size_t overflow_mask[8] = {0x0, 0x1249249, 0x2492492, 0x36db6db, 0x4924924, 0x5b6db6d, 0x6db6db6, 0x7ffffff};
void clamp(size_t* code) {
    * code &= ~ underflow_mask[(* code >> 0x1b & 0x7)];
    size_t mask = * code >> 0x1b & 0x1ffffffff;
    * code |= overflow_mask[((mask >> 0x0 | mask >> 0x3 | mask >> 0x6 | mask >> 0x9 | mask >> 0xc | mask >> 0xf | mask >> 0x12 | mask >> 0x15 | mask >> 0x18 | mask >> 0x1b | mask >> 0x1e) & 0x7)];
    * code &= 0x7ffffff;
};


const size_t lookup_table[0x3][512] = {{0x0, 0x1, 0x8, 0x9, 0x40, 0x41, 0x48, 0x49, 0x200, 0x201, 0x208, 0x209, 0x240, 0x241, 0x248, 0x249, 0x1000, 0x1001, 0x1008, 0x1009, 0x1040, 0x1041, 0x1048, 0x1049, 0x1200, 0x1201, 0x1208, 0x1209, 0x1240, 0x1241, 0x1248, 0x1249, 0x8000, 0x8001, 0x8008, 0x8009, 0x8040, 0x8041, 0x8048, 0x8049, 0x8200, 0x8201, 0x8208, 0x8209, 0x8240, 0x8241, 0x8248, 0x8249, 0x9000, 0x9001, 0x9008, 0x9009, 0x9040, 0x9041, 0x9048, 0x9049, 0x9200, 0x9201, 0x9208, 0x9209, 0x9240, 0x9241, 0x9248, 0x9249, 0x40000, 0x40001, 0x40008, 0x40009, 0x40040, 0x40041, 0x40048, 0x40049, 0x40200, 0x40201, 0x40208, 0x40209, 0x40240, 0x40241, 0x40248, 0x40249, 0x41000, 0x41001, 0x41008, 0x41009, 0x41040, 0x41041, 0x41048, 0x41049, 0x41200, 0x41201, 0x41208, 0x41209, 0x41240, 0x41241, 0x41248, 0x41249, 0x48000, 0x48001, 0x48008, 0x48009, 0x48040, 0x48041, 0x48048, 0x48049, 0x48200, 0x48201, 0x48208, 0x48209, 0x48240, 0x48241, 0x48248, 0x48249, 0x49000, 0x49001, 0x49008, 0x49009, 0x49040, 0x49041, 0x49048, 0x49049, 0x49200, 0x49201, 0x49208, 0x49209, 0x49240, 0x49241, 0x49248, 0x49249, 0x200000, 0x200001, 0x200008, 0x200009, 0x200040, 0x200041, 0x200048, 0x200049, 0x200200, 0x200201, 0x200208, 0x200209, 0x200240, 0x200241, 0x200248, 0x200249, 0x201000, 0x201001, 0x201008, 0x201009, 0x201040, 0x201041, 0x201048, 0x201049, 0x201200, 0x201201, 0x201208, 0x201209, 0x201240, 0x201241, 0x201248, 0x201249, 0x208000, 0x208001, 0x208008, 0x208009, 0x208040, 0x208041, 0x208048, 0x208049, 0x208200, 0x208201, 0x208208, 0x208209, 0x208240, 0x208241, 0x208248, 0x208249, 0x209000, 0x209001, 0x209008, 0x209009, 0x209040, 0x209041, 0x209048, 0x209049, 0x209200, 0x209201, 0x209208, 0x209209, 0x209240, 0x209241, 0x209248, 0x209249, 0x240000, 0x240001, 0x240008, 0x240009, 0x240040, 0x240041, 0x240048, 0x240049, 0x240200, 0x240201, 0x240208, 0x240209, 0x240240, 0x240241, 0x240248, 0x240249, 0x241000, 0x241001, 0x241008, 0x241009, 0x241040, 0x241041, 0x241048, 0x241049, 0x241200, 0x241201, 0x241208, 0x241209, 0x241240, 0x241241, 0x241248, 0x241249, 0x248000, 0x248001, 0x248008, 0x248009, 0x248040, 0x248041, 0x248048, 0x248049, 0x248200, 0x248201, 0x248208, 0x248209, 0x248240, 0x248241, 0x248248, 0x248249, 0x249000, 0x249001, 0x249008, 0x249009, 0x249040, 0x249041, 0x249048, 0x249049, 0x249200, 0x249201, 0x249208, 0x249209, 0x249240, 0x249241, 0x249248, 0x249249, 0x1000000, 0x1000001, 0x1000008, 0x1000009, 0x1000040, 0x1000041, 0x1000048, 0x1000049, 0x1000200, 0x1000201, 0x1000208, 0x1000209, 0x1000240, 0x1000241, 0x1000248, 0x1000249, 0x1001000, 0x1001001, 0x1001008, 0x1001009, 0x1001040, 0x1001041, 0x1001048, 0x1001049, 0x1001200, 0x1001201, 0x1001208, 0x1001209, 0x1001240, 0x1001241, 0x1001248, 0x1001249, 0x1008000, 0x1008001, 0x1008008, 0x1008009, 0x1008040, 0x1008041, 0x1008048, 0x1008049, 0x1008200, 0x1008201, 0x1008208, 0x1008209, 0x1008240, 0x1008241, 0x1008248, 0x1008249, 0x1009000, 0x1009001, 0x1009008, 0x1009009, 0x1009040, 0x1009041, 0x1009048, 0x1009049, 0x1009200, 0x1009201, 0x1009208, 0x1009209, 0x1009240, 0x1009241, 0x1009248, 0x1009249, 0x1040000, 0x1040001, 0x1040008, 0x1040009, 0x1040040, 0x1040041, 0x1040048, 0x1040049, 0x1040200, 0x1040201, 0x1040208, 0x1040209, 0x1040240, 0x1040241, 0x1040248, 0x1040249, 0x1041000, 0x1041001, 0x1041008, 0x1041009, 0x1041040, 0x1041041, 0x1041048, 0x1041049, 0x1041200, 0x1041201, 0x1041208, 0x1041209, 0x1041240, 0x1041241, 0x1041248, 0x1041249, 0x1048000, 0x1048001, 0x1048008, 0x1048009, 0x1048040, 0x1048041, 0x1048048, 0x1048049, 0x1048200, 0x1048201, 0x1048208, 0x1048209, 0x1048240, 0x1048241, 0x1048248, 0x1048249, 0x1049000, 0x1049001, 0x1049008, 0x1049009, 0x1049040, 0x1049041, 0x1049048, 0x1049049, 0x1049200, 0x1049201, 0x1049208, 0x1049209, 0x1049240, 0x1049241, 0x1049248, 0x1049249, 0x1200000, 0x1200001, 0x1200008, 0x1200009, 0x1200040, 0x1200041, 0x1200048, 0x1200049, 0x1200200, 0x1200201, 0x1200208, 0x1200209, 0x1200240, 0x1200241, 0x1200248, 0x1200249, 0x1201000, 0x1201001, 0x1201008, 0x1201009, 0x1201040, 0x1201041, 0x1201048, 0x1201049, 0x1201200, 0x1201201, 0x1201208, 0x1201209, 0x1201240, 0x1201241, 0x1201248, 0x1201249, 0x1208000, 0x1208001, 0x1208008, 0x1208009, 0x1208040, 0x1208041, 0x1208048, 0x1208049, 0x1208200, 0x1208201, 0x1208208, 0x1208209, 0x1208240, 0x1208241, 0x1208248, 0x1208249, 0x1209000, 0x1209001, 0x1209008, 0x1209009, 0x1209040, 0x1209041, 0x1209048, 0x1209049, 0x1209200, 0x1209201, 0x1209208, 0x1209209, 0x1209240, 0x1209241, 0x1209248, 0x1209249, 0x1240000, 0x1240001, 0x1240008, 0x1240009, 0x1240040, 0x1240041, 0x1240048, 0x1240049, 0x1240200, 0x1240201, 0x1240208, 0x1240209, 0x1240240, 0x1240241, 0x1240248, 0x1240249, 0x1241000, 0x1241001, 0x1241008, 0x1241009, 0x1241040, 0x1241041, 0x1241048, 0x1241049, 0x1241200, 0x1241201, 0x1241208, 0x1241209, 0x1241240, 0x1241241, 0x1241248, 0x1241249, 0x1248000, 0x1248001, 0x1248008, 0x1248009, 0x1248040, 0x1248041, 0x1248048, 0x1248049, 0x1248200, 0x1248201, 0x1248208, 0x1248209, 0x1248240, 0x1248241, 0x1248248, 0x1248249, 0x1249000, 0x1249001, 0x1249008, 0x1249009, 0x1249040, 0x1249041, 0x1249048, 0x1249049, 0x1249200, 0x1249201, 0x1249208, 0x1249209, 0x1249240, 0x1249241, 0x1249248, 0x1249249}, {0x0, 0x2, 0x10, 0x12, 0x80, 0x82, 0x90, 0x92, 0x400, 0x402, 0x410, 0x412, 0x480, 0x482, 0x490, 0x492, 0x2000, 0x2002, 0x2010, 0x2012, 0x2080, 0x2082, 0x2090, 0x2092, 0x2400, 0x2402, 0x2410, 0x2412, 0x2480, 0x2482, 0x2490, 0x2492, 0x10000, 0x10002, 0x10010, 0x10012, 0x10080, 0x10082, 0x10090, 0x10092, 0x10400, 0x10402, 0x10410, 0x10412, 0x10480, 0x10482, 0x10490, 0x10492, 0x12000, 0x12002, 0x12010, 0x12012, 0x12080, 0x12082, 0x12090, 0x12092, 0x12400, 0x12402, 0x12410, 0x12412, 0x12480, 0x12482, 0x12490, 0x12492, 0x80000, 0x80002, 0x80010, 0x80012, 0x80080, 0x80082, 0x80090, 0x80092, 0x80400, 0x80402, 0x80410, 0x80412, 0x80480, 0x80482, 0x80490, 0x80492, 0x82000, 0x82002, 0x82010, 0x82012, 0x82080, 0x82082, 0x82090, 0x82092, 0x82400, 0x82402, 0x82410, 0x82412, 0x82480, 0x82482, 0x82490, 0x82492, 0x90000, 0x90002, 0x90010, 0x90012, 0x90080, 0x90082, 0x90090, 0x90092, 0x90400, 0x90402, 0x90410, 0x90412, 0x90480, 0x90482, 0x90490, 0x90492, 0x92000, 0x92002, 0x92010, 0x92012, 0x92080, 0x92082, 0x92090, 0x92092, 0x92400, 0x92402, 0x92410, 0x92412, 0x92480, 0x92482, 0x92490, 0x92492, 0x400000, 0x400002, 0x400010, 0x400012, 0x400080, 0x400082, 0x400090, 0x400092, 0x400400, 0x400402, 0x400410, 0x400412, 0x400480, 0x400482, 0x400490, 0x400492, 0x402000, 0x402002, 0x402010, 0x402012, 0x402080, 0x402082, 0x402090, 0x402092, 0x402400, 0x402402, 0x402410, 0x402412, 0x402480, 0x402482, 0x402490, 0x402492, 0x410000, 0x410002, 0x410010, 0x410012, 0x410080, 0x410082, 0x410090, 0x410092, 0x410400, 0x410402, 0x410410, 0x410412, 0x410480, 0x410482, 0x410490, 0x410492, 0x412000, 0x412002, 0x412010, 0x412012, 0x412080, 0x412082, 0x412090, 0x412092, 0x412400, 0x412402, 0x412410, 0x412412, 0x412480, 0x412482, 0x412490, 0x412492, 0x480000, 0x480002, 0x480010, 0x480012, 0x480080, 0x480082, 0x480090, 0x480092, 0x480400, 0x480402, 0x480410, 0x480412, 0x480480, 0x480482, 0x480490, 0x480492, 0x482000, 0x482002, 0x482010, 0x482012, 0x482080, 0x482082, 0x482090, 0x482092, 0x482400, 0x482402, 0x482410, 0x482412, 0x482480, 0x482482, 0x482490, 0x482492, 0x490000, 0x490002, 0x490010, 0x490012, 0x490080, 0x490082, 0x490090, 0x490092, 0x490400, 0x490402, 0x490410, 0x490412, 0x490480, 0x490482, 0x490490, 0x490492, 0x492000, 0x492002, 0x492010, 0x492012, 0x492080, 0x492082, 0x492090, 0x492092, 0x492400, 0x492402, 0x492410, 0x492412, 0x492480, 0x492482, 0x492490, 0x492492, 0x2000000, 0x2000002, 0x2000010, 0x2000012, 0x2000080, 0x2000082, 0x2000090, 0x2000092, 0x2000400, 0x2000402, 0x2000410, 0x2000412, 0x2000480, 0x2000482, 0x2000490, 0x2000492, 0x2002000, 0x2002002, 0x2002010, 0x2002012, 0x2002080, 0x2002082, 0x2002090, 0x2002092, 0x2002400, 0x2002402, 0x2002410, 0x2002412, 0x2002480, 0x2002482, 0x2002490, 0x2002492, 0x2010000, 0x2010002, 0x2010010, 0x2010012, 0x2010080, 0x2010082, 0x2010090, 0x2010092, 0x2010400, 0x2010402, 0x2010410, 0x2010412, 0x2010480, 0x2010482, 0x2010490, 0x2010492, 0x2012000, 0x2012002, 0x2012010, 0x2012012, 0x2012080, 0x2012082, 0x2012090, 0x2012092, 0x2012400, 0x2012402, 0x2012410, 0x2012412, 0x2012480, 0x2012482, 0x2012490, 0x2012492, 0x2080000, 0x2080002, 0x2080010, 0x2080012, 0x2080080, 0x2080082, 0x2080090, 0x2080092, 0x2080400, 0x2080402, 0x2080410, 0x2080412, 0x2080480, 0x2080482, 0x2080490, 0x2080492, 0x2082000, 0x2082002, 0x2082010, 0x2082012, 0x2082080, 0x2082082, 0x2082090, 0x2082092, 0x2082400, 0x2082402, 0x2082410, 0x2082412, 0x2082480, 0x2082482, 0x2082490, 0x2082492, 0x2090000, 0x2090002, 0x2090010, 0x2090012, 0x2090080, 0x2090082, 0x2090090, 0x2090092, 0x2090400, 0x2090402, 0x2090410, 0x2090412, 0x2090480, 0x2090482, 0x2090490, 0x2090492, 0x2092000, 0x2092002, 0x2092010, 0x2092012, 0x2092080, 0x2092082, 0x2092090, 0x2092092, 0x2092400, 0x2092402, 0x2092410, 0x2092412, 0x2092480, 0x2092482, 0x2092490, 0x2092492, 0x2400000, 0x2400002, 0x2400010, 0x2400012, 0x2400080, 0x2400082, 0x2400090, 0x2400092, 0x2400400, 0x2400402, 0x2400410, 0x2400412, 0x2400480, 0x2400482, 0x2400490, 0x2400492, 0x2402000, 0x2402002, 0x2402010, 0x2402012, 0x2402080, 0x2402082, 0x2402090, 0x2402092, 0x2402400, 0x2402402, 0x2402410, 0x2402412, 0x2402480, 0x2402482, 0x2402490, 0x2402492, 0x2410000, 0x2410002, 0x2410010, 0x2410012, 0x2410080, 0x2410082, 0x2410090, 0x2410092, 0x2410400, 0x2410402, 0x2410410, 0x2410412, 0x2410480, 0x2410482, 0x2410490, 0x2410492, 0x2412000, 0x2412002, 0x2412010, 0x2412012, 0x2412080, 0x2412082, 0x2412090, 0x2412092, 0x2412400, 0x2412402, 0x2412410, 0x2412412, 0x2412480, 0x2412482, 0x2412490, 0x2412492, 0x2480000, 0x2480002, 0x2480010, 0x2480012, 0x2480080, 0x2480082, 0x2480090, 0x2480092, 0x2480400, 0x2480402, 0x2480410, 0x2480412, 0x2480480, 0x2480482, 0x2480490, 0x2480492, 0x2482000, 0x2482002, 0x2482010, 0x2482012, 0x2482080, 0x2482082, 0x2482090, 0x2482092, 0x2482400, 0x2482402, 0x2482410, 0x2482412, 0x2482480, 0x2482482, 0x2482490, 0x2482492, 0x2490000, 0x2490002, 0x2490010, 0x2490012, 0x2490080, 0x2490082, 0x2490090, 0x2490092, 0x2490400, 0x2490402, 0x2490410, 0x2490412, 0x2490480, 0x2490482, 0x2490490, 0x2490492, 0x2492000, 0x2492002, 0x2492010, 0x2492012, 0x2492080, 0x2492082, 0x2492090, 0x2492092, 0x2492400, 0x2492402, 0x2492410, 0x2492412, 0x2492480, 0x2492482, 0x2492490, 0x2492492}, {0x0, 0x4, 0x20, 0x24, 0x100, 0x104, 0x120, 0x124, 0x800, 0x804, 0x820, 0x824, 0x900, 0x904, 0x920, 0x924, 0x4000, 0x4004, 0x4020, 0x4024, 0x4100, 0x4104, 0x4120, 0x4124, 0x4800, 0x4804, 0x4820, 0x4824, 0x4900, 0x4904, 0x4920, 0x4924, 0x20000, 0x20004, 0x20020, 0x20024, 0x20100, 0x20104, 0x20120, 0x20124, 0x20800, 0x20804, 0x20820, 0x20824, 0x20900, 0x20904, 0x20920, 0x20924, 0x24000, 0x24004, 0x24020, 0x24024, 0x24100, 0x24104, 0x24120, 0x24124, 0x24800, 0x24804, 0x24820, 0x24824, 0x24900, 0x24904, 0x24920, 0x24924, 0x100000, 0x100004, 0x100020, 0x100024, 0x100100, 0x100104, 0x100120, 0x100124, 0x100800, 0x100804, 0x100820, 0x100824, 0x100900, 0x100904, 0x100920, 0x100924, 0x104000, 0x104004, 0x104020, 0x104024, 0x104100, 0x104104, 0x104120, 0x104124, 0x104800, 0x104804, 0x104820, 0x104824, 0x104900, 0x104904, 0x104920, 0x104924, 0x120000, 0x120004, 0x120020, 0x120024, 0x120100, 0x120104, 0x120120, 0x120124, 0x120800, 0x120804, 0x120820, 0x120824, 0x120900, 0x120904, 0x120920, 0x120924, 0x124000, 0x124004, 0x124020, 0x124024, 0x124100, 0x124104, 0x124120, 0x124124, 0x124800, 0x124804, 0x124820, 0x124824, 0x124900, 0x124904, 0x124920, 0x124924, 0x800000, 0x800004, 0x800020, 0x800024, 0x800100, 0x800104, 0x800120, 0x800124, 0x800800, 0x800804, 0x800820, 0x800824, 0x800900, 0x800904, 0x800920, 0x800924, 0x804000, 0x804004, 0x804020, 0x804024, 0x804100, 0x804104, 0x804120, 0x804124, 0x804800, 0x804804, 0x804820, 0x804824, 0x804900, 0x804904, 0x804920, 0x804924, 0x820000, 0x820004, 0x820020, 0x820024, 0x820100, 0x820104, 0x820120, 0x820124, 0x820800, 0x820804, 0x820820, 0x820824, 0x820900, 0x820904, 0x820920, 0x820924, 0x824000, 0x824004, 0x824020, 0x824024, 0x824100, 0x824104, 0x824120, 0x824124, 0x824800, 0x824804, 0x824820, 0x824824, 0x824900, 0x824904, 0x824920, 0x824924, 0x900000, 0x900004, 0x900020, 0x900024, 0x900100, 0x900104, 0x900120, 0x900124, 0x900800, 0x900804, 0x900820, 0x900824, 0x900900, 0x900904, 0x900920, 0x900924, 0x904000, 0x904004, 0x904020, 0x904024, 0x904100, 0x904104, 0x904120, 0x904124, 0x904800, 0x904804, 0x904820, 0x904824, 0x904900, 0x904904, 0x904920, 0x904924, 0x920000, 0x920004, 0x920020, 0x920024, 0x920100, 0x920104, 0x920120, 0x920124, 0x920800, 0x920804, 0x920820, 0x920824, 0x920900, 0x920904, 0x920920, 0x920924, 0x924000, 0x924004, 0x924020, 0x924024, 0x924100, 0x924104, 0x924120, 0x924124, 0x924800, 0x924804, 0x924820, 0x924824, 0x924900, 0x924904, 0x924920, 0x924924, 0x4000000, 0x4000004, 0x4000020, 0x4000024, 0x4000100, 0x4000104, 0x4000120, 0x4000124, 0x4000800, 0x4000804, 0x4000820, 0x4000824, 0x4000900, 0x4000904, 0x4000920, 0x4000924, 0x4004000, 0x4004004, 0x4004020, 0x4004024, 0x4004100, 0x4004104, 0x4004120, 0x4004124, 0x4004800, 0x4004804, 0x4004820, 0x4004824, 0x4004900, 0x4004904, 0x4004920, 0x4004924, 0x4020000, 0x4020004, 0x4020020, 0x4020024, 0x4020100, 0x4020104, 0x4020120, 0x4020124, 0x4020800, 0x4020804, 0x4020820, 0x4020824, 0x4020900, 0x4020904, 0x4020920, 0x4020924, 0x4024000, 0x4024004, 0x4024020, 0x4024024, 0x4024100, 0x4024104, 0x4024120, 0x4024124, 0x4024800, 0x4024804, 0x4024820, 0x4024824, 0x4024900, 0x4024904, 0x4024920, 0x4024924, 0x4100000, 0x4100004, 0x4100020, 0x4100024, 0x4100100, 0x4100104, 0x4100120, 0x4100124, 0x4100800, 0x4100804, 0x4100820, 0x4100824, 0x4100900, 0x4100904, 0x4100920, 0x4100924, 0x4104000, 0x4104004, 0x4104020, 0x4104024, 0x4104100, 0x4104104, 0x4104120, 0x4104124, 0x4104800, 0x4104804, 0x4104820, 0x4104824, 0x4104900, 0x4104904, 0x4104920, 0x4104924, 0x4120000, 0x4120004, 0x4120020, 0x4120024, 0x4120100, 0x4120104, 0x4120120, 0x4120124, 0x4120800, 0x4120804, 0x4120820, 0x4120824, 0x4120900, 0x4120904, 0x4120920, 0x4120924, 0x4124000, 0x4124004, 0x4124020, 0x4124024, 0x4124100, 0x4124104, 0x4124120, 0x4124124, 0x4124800, 0x4124804, 0x4124820, 0x4124824, 0x4124900, 0x4124904, 0x4124920, 0x4124924, 0x4800000, 0x4800004, 0x4800020, 0x4800024, 0x4800100, 0x4800104, 0x4800120, 0x4800124, 0x4800800, 0x4800804, 0x4800820, 0x4800824, 0x4800900, 0x4800904, 0x4800920, 0x4800924, 0x4804000, 0x4804004, 0x4804020, 0x4804024, 0x4804100, 0x4804104, 0x4804120, 0x4804124, 0x4804800, 0x4804804, 0x4804820, 0x4804824, 0x4804900, 0x4804904, 0x4804920, 0x4804924, 0x4820000, 0x4820004, 0x4820020, 0x4820024, 0x4820100, 0x4820104, 0x4820120, 0x4820124, 0x4820800, 0x4820804, 0x4820820, 0x4820824, 0x4820900, 0x4820904, 0x4820920, 0x4820924, 0x4824000, 0x4824004, 0x4824020, 0x4824024, 0x4824100, 0x4824104, 0x4824120, 0x4824124, 0x4824800, 0x4824804, 0x4824820, 0x4824824, 0x4824900, 0x4824904, 0x4824920, 0x4824924, 0x4900000, 0x4900004, 0x4900020, 0x4900024, 0x4900100, 0x4900104, 0x4900120, 0x4900124, 0x4900800, 0x4900804, 0x4900820, 0x4900824, 0x4900900, 0x4900904, 0x4900920, 0x4900924, 0x4904000, 0x4904004, 0x4904020, 0x4904024, 0x4904100, 0x4904104, 0x4904120, 0x4904124, 0x4904800, 0x4904804, 0x4904820, 0x4904824, 0x4904900, 0x4904904, 0x4904920, 0x4904924, 0x4920000, 0x4920004, 0x4920020, 0x4920024, 0x4920100, 0x4920104, 0x4920120, 0x4920124, 0x4920800, 0x4920804, 0x4920820, 0x4920824, 0x4920900, 0x4920904, 0x4920920, 0x4920924, 0x4924000, 0x4924004, 0x4924020, 0x4924024, 0x4924100, 0x4924104, 0x4924120, 0x4924124, 0x4924800, 0x4924804, 0x4924820, 0x4924824, 0x4924900, 0x4924904, 0x4924920, 0x4924924}};
size_t encode(size_t* indices) {
    return (lookup_table[0x0][(indices[0x0] >> 0x0 & 0x1ff)] | lookup_table[0x1][(indices[0x1] >> 0x0 & 0x1ff)] | lookup_table[0x2][(indices[0x2] >> 0x0 & 0x1ff)]) << 0x0;
};


