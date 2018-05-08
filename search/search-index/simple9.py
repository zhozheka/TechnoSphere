import array
import struct

class simple9_list:
    def __init__(self, List=None):
        self.codes = { # code  #bit    #max    #number
                        1 << 28: [1,    1,        28],
                        2 << 28: [2,    3,        14],
                        3 << 28: [3,    7,         9],
                        4 << 28: [4,    15,        7],
                        5 << 28: [5,    31,        5],
                        6 << 28: [7,    127,       4],
                        7 << 28: [9,    511,       3],
                        8 << 28: [14,   16383,     2],
                        9 << 28: [28,   268435455, 1],
        }
        self.long_list = array.array('L')
        self.first_el = 0

        if List:
            self.compress_list(List)

    def encode_word(self, s, List):
        bit_, max_, num_ = self.codes[s << 28]

        word32 = 0
        word32 = word32 | s << 28  # set code

        for i in range(len(List)):
            word32 = word32 | List[i] << bit_*i

        return word32

    def decode_word(self, word32):
        s = word32 >> 28
        bit_, max_, num_ = self.codes[s << 28]
        List = []

        for i in range(num_):
            val = word32 >> bit_*i & max_
            if val == 0:
                break
            List.append(val)

        return List

    def compress_list(self, List):
        self.first_el = List[0]
        List_interval = []
        for i, j in zip(List[:-1], List[1:]):
            List_interval.append(j-i)

        i = 0
        self.long_list = array.array('L')

        while i<len(List_interval):
            for s in range(1,10):
                bit_, max_, num_ = self.codes[s << 28]

                if max(List_interval[i: i+num_] + [0]) > max_:
                    continue
                word32 = self.encode_word(s, List_interval[i: i+num_])
                self.long_list.append(word32)
                i += num_

    def decompress_list(self):
        decompressed_list = [self.first_el]
        for word32 in self.long_list:
            code = self.decode_word(word32)
            for n in code:
                decompressed_list.append(n+decompressed_list[-1])
        return decompressed_list

    def to_bytes(self):
        s = struct.pack('I', self.first_el) + self.long_list.tostring()
        return s

    def from_bytes(self, s):
        self.first_el = struct.unpack('I', s[:4])[0]  # 4 bytes
        self.long_list = array.array('L')
        self.long_list.fromstring(s[4:])
