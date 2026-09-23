"""Only the six UI glyphs required by the requested mixed-case title/FPS."""
GLYPHS={
    'v':('00000','00000','10001','10001','10001','01010','00100'),
    'i':('00100','00000','01100','00100','00100','00100','01110'),
    'b':('10000','10000','10110','11001','10001','10001','11110'),
    'e':('00000','00000','01110','10001','11111','10000','01111'),
    '.':('00000','00000','00000','00000','00000','00110','00110'),
    ':':('00000','00110','00110','00000','00110','00110','00000'),
}

def update_font(source):
    assert len(source)==2048
    out=bytearray(source)
    for char,rows in GLYPHS.items():
        out[ord(char)*8:ord(char)*8+8]=bytes([int(row,2)<<2 for row in rows]+[0])
    return bytes(out)
