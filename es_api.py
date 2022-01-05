# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import math
from tqdm import tqdm

# 连接
es = Elasticsearch()


# 删除索引
def delete_index(index):
    if es.indices.exists(index=index):
        es.indices.delete(index=index)
        return False
    return True


# 新增数据
def insert_test_data(index, doc_type):
    for i in range(1000):
        _body = {
            'author': 'kimchy' + str(i),
            'text': 'Elasticsearch: cool. bonsai cool.',
            'timestamp': datetime.now(),
        }
        es.index(index=index, doc_type=doc_type, id=i, body=_body)


# id查询
def find_by_id():
    response = es.get(index="test_index", doc_type='index', id=1)
    print('id查询结果：', response)


# 刷新
# es.indices.refresh(index="test_index")

# query 查询
def es_query():
    res = es.search(index="test_index", doc_type="index", body={"query": {"match_all": {}}})
    for hit in res['hits']['hits']:
        print("query查询结果：", hit["_source"])


# id更新
def update_by_id():
    es.update(index='test_index', doc_type='index', id='1', body={
        "doc": {
            'author': 'tom',
            'text': 'Elasticsearch: cool. bonsai cool.',
            'timestamp': datetime.now()
        }
    })


# 批量操作
def bulk_operation():
    bulk_list = [
        # 删除id=1
        {
            '_op_type': 'delete',
            '_index': 'test_index',
            '_type': 'index',
            '_id': 1,
        },
        # 新增数据
        {
            '_op_type': 'create',
            '_index': 'test_index',
            '_type': 'index',
            '_id': 999,
            "_source": {
                'author': 'kimchy999',
                'text': 'Elasticsearch: cool. bonsai cool.',
                'timestamp': datetime.now(),
            }
        },
        # 更新，覆盖原文档
        {
            '_op_type': 'index',
            '_index': 'test_index',
            '_type': 'index',
            '_id': 2,
            "_source": {"test_field": "replaced test2"}
        },
        # 根据id更新
        {
            '_op_type': 'update',
            '_index': 'test_index',
            '_type': 'index',
            '_id': 7,
            "_retry_on_conflict": 3,
            "doc": {
                'text': 'Elasticsearch: cool. bonsai cool.update cool.',
            }
        }
    ]

    response = helpers.bulk(es, bulk_list)
    print('批量操作执行结果（变更条数）：', response)


# 批量插入
def bulk_insert(index, doc_type, items):
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
    helpers.bulk(es, actions)


def scroll_read(index, doc_type, query_body):
    print('es scroll read')
    result = []
    # 查询首页，获取返回滚动id
    page = es.search(body=query_body, index=index, doc_type=doc_type, scroll="2m")
    # 滚动id
    sid = page['_scroll_id']
    # 查询页大小
    scroll_size = page['hits']['total']
    # 首页查询结果写入返回数组
    page_data = page['hits']['hits']
    for doc in page_data:
        result.append(doc['_source'])

    while (scroll_size > 0):
        page = es.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        page_data = page['hits']['hits']
        scroll_size = len(page_data)
        if scroll_size > 0:
            for doc in page_data:
                result.append(doc['_source'])
    return result


if __name__ == '__main__':
    # insert_test_data('test_index', 'index')
    # query_body = {"query": {"match_all": {}}, "size": 100}
    # scroll_read('test_index', 'index', query_body)
    # delete_index('test_index')
    items = [
        {'id': '111', 'name': '222'}
    ]
    bulk_insert('test_index', 'index', items)
    print()
