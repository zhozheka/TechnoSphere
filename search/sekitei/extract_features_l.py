
# coding: utf-8

# In[1]:


import sys
import re
import random
from operator import itemgetter
from urlparse import unquote
from collections import Counter



# In[2]:


def extract_param_fts(query):
    param_fts = []
    query = query.replace('\n', '')

    for p in query.split('&'):
        param_fts.append('param_name:' + str(p.split('=')[0]))
        param_fts.append('param:' + str(p))

    return param_fts


# In[27]:


def extract_path_fts(path):
    if len(path) == 0:
        return ['segments:0']
    path = path.replace('\n', '')
    path_fts = []
    segments_n = 0
    i = 0

    digit_ptrn = re.compile(r'\d+$')
    substr_ptrn = re.compile(r'[^\d]+\d+[^\d]+$')

    for seg in path.split('/'):
        if len(seg) == 0:
            continue
        segments_n += 1
        flag = False

        if len(seg.split('.')) == 1:
            path_fts.append('segment_name_' + str(i) + ':' + seg)

        if re.match(digit_ptrn, seg) is not None:
            path_fts.append('segment_[0-9]_' + str(i) + ':1')

        if re.match(substr_ptrn, seg) is not None:
            path_fts.append('segment_substr[0-9]_' + str(i) + ':1')
            flag = True

        if len(seg.split('.')) == 2:
            ext = seg.split('.')[1]

            if len(ext) != 0:
                if ext[-1] == '\n':
                    ext = ext[:-1]
                path_fts.append('segment_ext_' + str(i) + ':' + ext)
            if flag:
                path_fts.append('segment_ext_substr[0-9]_' + str(i) + ':' + str(len(seg)))

        path_fts.append('segment_len_' + str(i) + ':' + str(len(seg)))

        i += 1

    path_fts.append('segments:' + str(segments_n))


    return path_fts


# In[28]:


def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
    N_URLS = 2000
    BATCH_SIZE = 1000
    fts_list = []

    for INPUT_FILE in [INPUT_FILE_1, INPUT_FILE_2]:
        with open(INPUT_FILE) as f1:
            nums = random.sample(range(N_URLS), BATCH_SIZE)

            for n, s in enumerate(f1):
                if n not in nums:
                    continue

                s = unquote(s)


                host_pattern = re.compile('http://[^/]+/')
                if len(re.split(host_pattern, s)) <= 1:
                    continue
                right = re.split(host_pattern, s)[1]

                sp = re.split(r'\?', right)
                path = sp[0]
                if len(sp) == 2:
                    query = sp[1]
                else:
                    query = None

                if query is not None:
                    fts_list += extract_param_fts(query)

                if path is not None:
                    if len(path) > 0:
                        fts_list += extract_path_fts(path)

    fts = Counter(fts_list)
    with open(OUTPUT_FILE, 'w') as f_out:
        for fea, cnt in fts.most_common():
            if cnt < 100:
                break
            f_out.write(str(fea) + '\t' + str(cnt) + '\n')