# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

# 需求：获取ES全部索引的字段和类型，打印成markdown格式的表格

es = Elasticsearch()

# 索引字段中文映射
ch_name_map = {
    'id': 'ID',
    'age': '年龄'
}

# GET /_cat/indices?h=index
resp = es.cat.indices(h='index')
indices = resp.split('\n')
clean_indices = []
for index in indices:
    if index != '':
        # 排除'.' 开头的索引
        if bool(1 - index.startswith('.')):
            # 排除包含log 的索引
            if bool(1 - ('log' in index)):
                clean_indices.append(index)

# 遍历索引，获取mapping.properties
for index in clean_indices:
    resp = es.indices.get(index=index)
    aliases = dict(resp[index]['aliases'])
    aliases_str = ''
    for alias in aliases:
        aliases_str += alias + ', '
    mappings = resp[index]['mappings']
    for doc_key, doc_val in mappings.items():
        print('## '+index + '索引：')
        print('别名：'+aliases_str)
        print('|字段名|类型|中文|')
        print('|-|-|-|')
        for k, v in doc_val['properties'].items():
            if 'type' in v.keys():
                ch = ch_name_map[k] if k in ch_name_map.keys() else ''
                print('|%s|%s|%s|' % (k,v['type'],ch))

    print('')
