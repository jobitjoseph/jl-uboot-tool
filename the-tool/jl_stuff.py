#####################################
# Common JieLi stuff
#=====================================================

try:
    import crcmod

    jl_crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)

except ImportError:
    print("Warning: falling back to local jl_crc16 implementation, which is unoptimized.")
    print("Consider installing the crcmod package to enhance performance.")

    def jl_crc16(data, crc=0):
        for b in data:
            crc ^= b << 8
            for i in range(8):
                crc = ((crc << 1) ^ (0x1021 if (crc >> 15) else 0)) & 0xffff
        return crc

#=====================================================

#################################################################
# The Hyper Secret And The Most Sophisticated Encryption Algos! #
#################################################################

def jl_crypt(data, key=0xffff):
    data = bytearray(data)

    for i in range(len(data)):
        data[i] ^= key & 0xff
        key = ((key << 1) ^ (0x1021 if (key >> 15) else 0)) & 0xffff

    return bytes(data)

def jl_cryptcrc(data, key=0xffffffff):
    crc = key & 0xffff
    crc = jl_crc16(bytes([key >> 16 & 0xff, key >> 24 & 0xff]), crc)

    # GB2312 -> "孟黎我爱你，玉林" -- meng li i love you, yulin #
    magic = b'\xc3\xcf\xc0\xe8\xce\xd2\xb0\xae\xc4\xe3\xa3\xac\xd3\xf1\xc1\xd6'

    data = bytearray(data)

    for i in range(len(data)):
        crc = jl_crc16(bytes([magic[i % len(magic)]]), crc)
        data[i] ^= crc & 0xff

    return bytes(data)

#=====================================================

def hexdump(data, width=16):
    for i in range(0, len(data), width):
        s = '%8X: ' % i

        for j in range(width):
            if (i+j) < len(data):
                s += '%02X ' % data[i+j]
            else:
                s += '-- '

        s += ' |'

        for j in range(width):
            if (i+j) < len(data):
                c = data[i+j]
                if c < 0x20 or c >= 0x7f: c = ord('.')
                s += chr(c)
            else:
                s += ' '

        s += '|'

        print(s)
    print()