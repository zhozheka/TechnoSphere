#!/usr/bin/env python
# -*- coding: utf-8 -*-

import document_pb2
import struct
import gzip
import sys


class DocumentStreamReader:
    def __init__(self, files):
        self.files = files

    def __iter__(self):
        for file_ in self.files:
            self.stream = gzip.open(file_, 'rb')

            while True:
                sb = self.stream.read(4)
                if sb == '':
                    break

                size = struct.unpack('i', sb)[0]
                msg = self.stream.read(size)
                doc = document_pb2.document()
                doc.ParseFromString(msg)
                yield doc

