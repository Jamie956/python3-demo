# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers

# 本地连接
es = Elasticsearch()


# 连接指定地址
# es = Elasticsearch(['192.168.1.**'],http_auth=('**', '**'),port=9200)

# 删除索引
def delete_index():
    if es.indices.exists(index="test_index"):
        print("索引存在")
        response = es.indices.delete(index="test_index")
        print('删除索引执行结果:', response)


# 新增数据
def create_data():
    for i in range(10):
        _body = {
            'author': 'kimchy' + str(i),
            'text': 'Elasticsearch: cool. bonsai cool.',
            'timestamp': datetime.now(),
        }
        response = es.index(index="test_index", doc_type='index', id=i, body=_body)
        print('创建文档执行结果:', response)


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
    response = es.update(index='test_index', doc_type='index', id='1', body={
        "doc": {
            'author': 'tom',
            'text': 'Elasticsearch: cool. bonsai cool.',
            'timestamp': datetime.now()
        }
    })


# 批量更新
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

def scroll_read():
    # 新增数据
    # doc = {
    #     'author': 'kimchy',
    #     'text': 'Elasticsearch: cool. bonsai cool.',
    #     'timestamp': datetime.now(),
    # }
    # for i in range(200):
    #     es.index(index="test_index", body=doc)

    # 查询首页，获取返回滚动id
    page = es.search(body={"query": {"match_all": {}}, "size": 100}, index="test_index", doc_type="index", scroll="2m")
    # 滚动id
    sid = page['_scroll_id']
    # 查询页大小
    scroll_size = page['hits']['total']

    while (scroll_size > 0):
        start = datetime.now()
        page = es.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        # 命中数据条数
        scroll_size = len(page['hits']['hits'])
        print('页查询', str(scroll_size), '条', '消耗时间（毫秒）', (datetime.now() - start).microseconds)

if __name__ == '__main__':
    # delete_index()
    # create_data()
    # find_by_id()
    # es_query()
    # update_by_id()
    # bulk_operation()
    scroll_read()
