 # coding: utf-8


import sys
import os
import re
import random
import time
#from sklearn.cluster import <any cluster algorithm>
import numpy as np
from urlparse import unquote
import re
from scipy.spatial.distance import cdist
from mlxtend.preprocessing import OnehotTransactions
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans



def check_number(param):
    if re.match('^\d+$', param) != None:
        return True

    else:
        return False

def check_extension(param):
    if len(param.split('.')) > 1:
        return param.split('.')[-1]
    else:
        return None

def check_substr(param):
    if re.match('[^\d]+\d+[^\d]+$', param) != None:
        return True

    else:
        return False

def get_prop(url):


    D = {}
    properties = []

    #prepare
    url = url[7:][:-1]

    if url[-1] == '/':
        url = url[:-1]

    url = unquote(url)
    # fragment
    #url = url.split('#')[0]

    # query
    split_query = url.split('?')

    if len(split_query) > 1:
        D['query'] = split_query[1]
    else:
        D['query'] = ""

    #path
    D['url'] = split_query[0]
    if D['url'][-1] == '/':
        D['url'] = D['url'][:-1]

    D['path'] = D['url'].split('/')[1:]

    D['segments'] = len(D['path'])

    D['query_param'] = []
    D['query_param_value'] = []
    params = D['query'].split('&')
    for p in params:
        if p == '':
            continue
        D['query_param'].append(p.split('=')[0])
        D['query_param_value'].append(p)

    #generate features
    #1
    properties.append('segments:' + str(len(D['path'])))

    #2
    for param in D['query_param']:
        properties.append('param:' + param)

    #3
    for param in D['query_param_value']:
        properties.append('param:' + param)

    for i, string in enumerate(D['path']):

    #4a
        properties.append('segment_name_' + str(i) + ':' + string)

    #4b
        if check_number(string):
            properties.append('segment_[0-9]_' + str(i) + ':1')


    #4c

        CE = check_extension(string)
        CS = check_substr(string)

        if CS:
            properties.append('segment_substr[0-9]_' + str(i) + ':1')

    #4d
        if CE:
            properties.append('segment_ext_' + str(i) + ':' + CE)

    #4e
        if CE and CS:
            properties.append('segment_ext_substr[0-9]_' + str(i) + ':' + CE )

    #4f
        properties.append('segment_len_' + str(i) + ':' + str(len(string)))

    return properties



sekitei = None;

def define_segments(QLINK_URLS, UNKNOWN_URLS, QUOTA):
    global OH, lr, quota, i, km, part
    quota = QUOTA
    list_q = []
    obj_q = []
    for url in QLINK_URLS:
        prop = get_prop(url)
        list_q += prop
        obj_q.append(prop)


    params, count = np.unique(list_q, return_counts=True)
    params = np.array(params, dtype='object')
    count = np.array(count, dtype='object')
    feat_q_num = np.hstack((params.reshape(-1,1), count.reshape(-1,1)))
    feat_q_num =  feat_q_num[np.argsort(feat_q_num[:,1])]
    feat_q_num = feat_q_num[::-1]

    obj_g = []

    for url in UNKNOWN_URLS:
        prop = get_prop(url)
        obj_g.append(prop)


    imp_features = (feat_q_num[:100][:,0]).reshape(-1,1)


    OH = OnehotTransactions()
    OH.fit(imp_features)

    q_matrix = OH.transform(obj_q)
    g_matrix = OH.transform(obj_g)


    X = np.vstack((q_matrix, g_matrix))
    y = [1]*500 + [0]*500
    y = np.array(y)

    lr =  LinearRegression()
    lr.fit(X,y)
    i = 0

## divide by n clusters set part for each one
    n = 15
    km = KMeans(n_clusters=n)
    a = np.hstack((km.fit_predict(X).reshape(-1,1), y.reshape(-1,1)))
    part = np.zeros(n)
    for i in range(n):
        part[i] = a[a[:,0] == i][:,1].sum()
    part /= part.sum()


def fetch_url(url):

    global lr, OH, i, part, km
    prop = get_prop(url)
    oh_url = OH.transform([prop])
    pred = lr.predict(oh_url)
    quota_for_clusters = part*quota
    number_in_cluster = np.zeros(km.n_clusters)

    if pred > 0.15:
        pred_cluster = km.predict(oh_url)
        if number_in_cluster[pred_cluster] < quota_for_clusters[pred_cluster]:
            number_in_cluster[pred_cluster] +=1
            return True
        else:
            return False

    else:
        return False


    # global thr, q_matrix, OH
    # prop = get_prop(url)
    #
    # oh_url = OH.transform([prop])
    # val = cdist(q_matrix, oh_url).mean()
    #
    #
    # #return True
    # if val < thr:
    #     return True
    # else:
    #     return False
