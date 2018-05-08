import array
import struct

class varbyte_list:
    def __init__(self, List=None):
        self.bytes_list = array.array('B')
        self.first_el = 0
        self.iter = 0

        if List:
            self.compress_list(List)

    def encode_number(self, number):
        assert (number > 0)
        code = array.array('B')
        if number == 0:
            code.append(128)

        while number > 0:
            code.append(number%128)
            number = (number // 128)

        code = code[::-1]
        code[-1] = code[-1] | 128
        return code

    def decode_number(self, code):
        number = code[-1]-128
        p = 1
        for i in code[::-1][1:]:
            number += i * 128**p
            p += 1
        return number

    def compress_list(self, List):
        self.bytes_list = array.array('B')
        self.first_el = List[0]
        List_interval = []
        for i, j in zip(List[:-1], List[1:]):
            List_interval.append(j-i)

        for number in List_interval:
            self.bytes_list += (self.encode_number(number))

    def decompress_list(self):
        code = []
        List = [self.first_el]
        for l in self.bytes_list:
            code.append(l)
            if l > 127:
                List.append(self.decode_number(code) + List[-1])
                code = []
        return List

    def to_bytes(self):
        s = struct.pack('I', self.first_el) + self.bytes_list.tostring()
        return s

    def from_bytes(self, s):
        self.first_el = struct.unpack('I', s[:4])[0]  # 4 bytes
        self.bytes_list = array.array('B')
        self.bytes_list.fromstring(s[4:])
