# -*- coding: utf-8 -*-
import sys
import array
from varbyte import varbyte_list
from simple9 import simple9_list
import qtree
import time


def get_docid(query):
    f = open('./pickle/bin.txt', 'rb')

    # get position and length and read from bin
    ptr, len_ = bin_index[query]
    f.seek(ptr)
    bytes = f.read(len_)

    f.close()

    if compression_type == 'varbyte':
        vb = varbyte_list()
        vb.from_bytes(bytes)
        return vb.decompress_list()

    elif compression_type == 'simple9':
        s9 = simple9_list()
        s9.from_bytes(bytes)
        return s9.decompress_list()


def create_set(vertice, root=True):

    # build set from tree using De Morgan's laws
    # attr: 1 - is set, -1 is inverted set
    if vertice.is_operator:
        if vertice == '!':
            attr = 'invert'
            R, R_attr = create_set(vertice.right)
            return [R, -1 * R_attr]

        if vertice == '|':
            L, L_attr = create_set(vertice.left, root=False)
            R, R_attr = create_set(vertice.right, root=False)

            if L_attr == 1 and R_attr == 1:
                return [L | R, 1]

            if L_attr == -1 and R_attr == 1:
                return [L - R, -1]

            if L_attr == 1 and R_attr == -1:
                return [R - L, -1]

            if L_attr == -1 and R_attr == -1:
                return [L & R, -1]

        if vertice == '&':
            L, L_attr = create_set(vertice.left, root=False)
            R, R_attr = create_set(vertice.right, root=False)

            if L_attr == 1 and R_attr == 1:
                return [L & R, 1]

            if L_attr == -1 and R_attr == 1:
                return [R - L, 1]

            if L_attr == 1 and R_attr == -1:
                return [L - R, 1]

            if L_attr == -1 and R_attr == -1:
                return [L | R, -1]

    if vertice.is_term:
        key = vertice.value

        return [set(get_docid(key)), 1]


def parse_(query):
    query = query.lower()
    tree = qtree.build_query_tree(qtree.tokenize_query(query))
    s, attr = create_set(tree)
    assert(attr == 1)
    return s


def get_urls(query):

    url_idx = list(parse_(query.decode('utf-8')))
    url_idx.sort()

    urls = []
    for j, url in enumerate(index_url):
        if j in url_idx:
            urls.append(url)

    return len(urls), urls


# -------------------------

# read params
f = open('./pickle/params.txt', 'r')
compression_type = f.readline()
f.close()


# read urls
index_url = []
f = open('./pickle/urls.txt', 'r')
for line in f:
    index_url.append(line[:-1])
f.close()

# read bin index

bin_index = {}
f = open('./pickle/index_bin.txt', 'r')
for line in f:
    spl = line[:-1].split(' ')

    term = spl[0]
    ptr = int(spl[1])
    len_ = int(spl[2])

    bin_index[term] = (ptr, len_)

f.close()


# start search
while True:
    query = sys.stdin.readline()
    t0 = time.time()
    if not query:
        break

    query = query[:-1]
    print query

    num, urls = get_urls(query)

    print num
    for url in urls:
        print url