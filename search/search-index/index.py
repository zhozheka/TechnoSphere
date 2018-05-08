import sys
import cPickle

sys.path.append('./ts-idx-2018-master/')
import docreader, doc2words


argv = sys.argv

# name varbyte files ....
assert (len(argv) >= 3)


compression_type = argv[1]
assert (compression_type == 'varbyte' or compression_type == 'simple9')

files_gz = argv[2:]


docReader = docreader.DocumentStreamReader(files_gz)

# parse texts and create index
print 'parse text'
index_dict = {}
index_url = []
for idx, doc in enumerate(docReader):
    words = doc2words.extract_words(doc.text)
    index_url.append(doc.url)

    for word in words:
        if word in index_dict:
            if index_dict[word][-1] != idx:
                index_dict[word].append(idx)
        else:
            index_dict[word] = [idx]


# save to pickle
cPickle.dump(index_dict, open('./pickle/index_dict.p', 'w'))


# write urls
f = open('pickle/urls.txt', 'w')
for url in index_url:
    f.write(url)
    f.write('\n')
f.close()

# write params
f = open('pickle/params.txt', 'w')
f.write(compression_type)
f.close()
