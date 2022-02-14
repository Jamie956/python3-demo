from elasticsearch import Elasticsearch
from elasticsearch import helpers
import math
import time


def get_client(config):
    return Elasticsearch([config['host']], http_auth=(config['user'], config['pwd']), port=config['port'])


# 获取文档的全部字段
def mapping_fields(client, index, doc_type):
    fields = []
    mapping = client.indices.get_mapping(index=index)
    for key in mapping:
        if index in key:
            mapping_properties = mapping[key]["mappings"][doc_type]["properties"]
            for mapping_property in mapping_properties:
                fields.append(mapping_property)
    return fields


# 创建索引
def create_index(client, index_name, index_body):
    index_name = index_name + '_' + str(int(time.time()))
    client.indices.create(index=index_name, body=index_body)
    print("create index " + index_name)
    return index_name


def re_index(src_client, src_index, target_client, target_index):
    query_body = {"query": {"match_all": {}}, "size": 500}
    data = scroll_read(src_client, src_index, 'index', query_body)
    bulk_insert(target_client, target_index, 'index', data)


# 批量插入
def bulk_insert(client, index, doc_type, items):
    batch_size = 500
    total = len(items)
    segment = math.ceil(total / batch_size)
    actions = []

    for i in range(segment):
        start = i * batch_size
        end = total if (start + batch_size) > total else start + batch_size
        for j in range(start, end):
            action = {
                "_index": index,
                "_type": doc_type,
                "_id": items[j]['id'],
                "_source": items[j]
            }
            actions.append(action)
    helpers.bulk(client, actions)


# 批量更新
def bulk_update(client, index, doc_type, items, field):
    batch_size = 500
    total = len(items)
    segment = math.ceil(total / batch_size)
    actions = []

    for i in range(segment):
        start = i * batch_size
        end = total if (start + batch_size) > total else start + batch_size
        for j in range(start, end):
            action = {
                '_op_type': 'update',
                "_index": index,
                "_type": doc_type,
                "_id": items[j]['id'],
                "_retry_on_conflict": 3,
                "doc": {
                    field: items[j][field],
                }
            }
            actions.append(action)
    helpers.bulk(client, actions)


def scroll_read(client, index, doc_type, query_body):
    print('es scroll read')
    result = []
    # 查询首页，获取返回滚动id
    page = client.search(body=query_body, index=index, doc_type=doc_type, scroll="2m")
    # 滚动id
    sid = page['_scroll_id']
    # 查询页大小
    scroll_size = page['hits']['total']
    # 首页查询结果写入返回数组
    page_data = page['hits']['hits']
    for doc in page_data:
        result.append(doc['_source'])

    while (scroll_size > 0):
        page = client.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        page_data = page['hits']['hits']
        scroll_size = len(page_data)
        if scroll_size > 0:
            for doc in page_data:
                result.append(doc['_source'])
    return result

# 获取ES全部索引的字段和类型，打印成markdown格式的表格
def print_index():
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
            print('## ' + index + '索引：')
            print('别名：' + aliases_str)
            print('|字段名|类型|中文|')
            print('|-|-|-|')
            for k, v in doc_val['properties'].items():
                if 'type' in v.keys():
                    ch = ch_name_map[k] if k in ch_name_map.keys() else ''
                    print('|%s|%s|%s|' % (k, v['type'], ch))

        print('')

def update_by_id(client, index, id, doc):
    client.update(index=index, doc_type='index', id=id, body={"doc": doc})

def exist(client, index, id):
    return client.exists(index=index, doc_type="index", id=id)

if __name__ == '__main__':
    cf = {
        'host': '',
        'port': '',
        'user': '',
        'pwd': ''
    }
    client = get_client(cf)