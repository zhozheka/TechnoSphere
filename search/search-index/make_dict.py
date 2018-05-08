# -*- coding: utf-8 -*-
import cPickle
from varbyte import varbyte_list
from simple9 import simple9_list

# load params
f = open('./pickle/params.txt', 'r')
compression_type = f.readline()
f.close()

# load index
index_dict = cPickle.load(open('./pickle/index_dict.p', 'r'))


# write bin code
f = open('./pickle/bin.txt', 'w')
ptr = 0
index_bin = {}
for key in index_dict:

    # compress list using varbyte or simple9
    # encode compressed list to string
    # write this string to file and save position and length

    if compression_type == 'varbyte':
        vb = varbyte_list(index_dict[key])
        bytes_ = vb.to_bytes()

    elif compression_type == 'simple9':
        s9 = simple9_list(index_dict[key])
        bytes_ = s9.to_bytes()

    index_bin[key] = (ptr, len(bytes_))
    ptr += len(bytes_)
    f.write(bytes_)
f.close()


# write bin index
f = open('./pickle/index_bin.txt', 'w')

for key in index_bin:
    ptr, len_ = index_bin[key]
    f.write((key + ' ' + str(ptr) + ' ' + str(len_) + '\n').encode('utf-8'))

f.close()
