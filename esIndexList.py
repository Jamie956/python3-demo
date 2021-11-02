# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

# 需求：获取ES全部索引的字段和类型，打印成markdown格式的表格

es = Elasticsearch()

# GET /_cat/indices?h=index
resp = es.cat.indices(h='index')
indices = resp.split('\n')
clean_indices = []
for index in indices:
    if index != '':
        if bool(1-index.startswith('.')):
            clean_indices.append(index)

# 遍历多个索引，获取mapping.properties
for index in clean_indices:
    resp = es.indices.get_mapping(index=index)
    mappings = resp[index]['mappings']
    for doc_key,doc_val in mappings.items():
        print(index + '/' + doc_key)
        print('|字段名|类型|中文|')
        print('|-|-|-|')
        for k,v in doc_val['properties'].items():
            if 'type' in v.keys():
                print('|%s|%s||' % (k,v['type']))

    print('')
