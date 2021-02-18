from .ReadHelper import read_int_8, read_int_24be, read_int_24le, read_int_16le, signed24
from .EmbThread import EmbThread

PC_SIZE_CONVERSION_RATIO = 5.0 / 3.0

PCS_HOOPSIZE = {0:('PCD',(1,1)),,
               1:('PCQ (MAXI)',(1,1)),
               2:('PCS small hoop (80x80)',(80,80)),
               3:('PCS with large hoop (115x120)',(115,120)), #per Embroidermodder/libembroidery/format-pcs.c
               }

def read_pc_file(f, out, settings=None):
    version = read_int_8(f)
    hoop_size = read_int_8(f)
    hoop_size = PCS_HOOPSIZE[hoop_size]
    color_count = read_int_16le(f)
    for i in range(0, color_count):
        thread = EmbThread()
        thread.color = read_int_24be(f)
        out.add_thread(thread)
        mystery_byte = read_int_8(f) #FIXME: name this variable to something useful

    stitch_count = read_int_16le(f)
    while True:
        c0 = read_int_8(f)
        x = read_int_24le(f)
        c1 = read_int_8(f)
        y = read_int_24le(f)
        ctrl = read_int_8(f)
        if ctrl is None: break
        x = signed24(x)
        y = -signed24(y)
        x *= PC_SIZE_CONVERSION_RATIO
        y *= PC_SIZE_CONVERSION_RATIO
        #coverage  b00 00 00 00
        #stich_abs  00 00 00 00
        #color_chan ?? ?? ?? ?1
        #move_abs   ?? ?? ?1 ??
        if ctrl == 0x00:
            out.stitch_abs(x, y)
            continue
        if ctrl & 0x01:
            #FIXME: if we read a color lookup table above this ctrl probably changes to some specified color  
            out.color_change()
            continue
        if ctrl & 0x04:
            out.move_abs(x, y)
            continue
        break  # Uncaught Control
    out.end()


def read(f, out, settings=None):
    read_pc_file(f, out)
