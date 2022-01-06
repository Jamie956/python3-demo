# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import math
import time


# 连接
def connect(config):
    return Elasticsearch([config['host']], http_auth=(config['user'], config['pwd']), port=config['port'])


# 删除索引
def delete_index(client, index):
    if client.indices.exists(index=index):
        client.indices.delete(index=index)
        return False
    return True


# 新增数据
def insert_test_data(client, index, doc_type):
    for i in range(1000):
        _body = {
            'author': 'kimchy' + str(i),
            'text': 'Elasticsearch: cool. bonsai cool.',
            'timestamp': datetime.now(),
        }
        client.index(index=index, doc_type=doc_type, id=i, body=_body)


# id查询
def find_by_id(client):
    response = client.get(index="test_index", doc_type='index', id=1)
    print('id查询结果：', response)


# 刷新
# es.indices.refresh(index="test_index")

# query 查询
def es_query(client):
    res = client.search(index="test_index", doc_type="index", body={"query": {"match_all": {}}})
    for hit in res['hits']['hits']:
        print("query查询结果：", hit["_source"])


# id更新
def update_by_id(client):
    client.update(index='test_index', doc_type='index', id='1', body={
        "doc": {
            'author': 'tom',
            'text': 'Elasticsearch: cool. bonsai cool.',
            'timestamp': datetime.now()
        }
    })


# 批量操作
def bulk_operation(client):
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

    response = helpers.bulk(client, bulk_list)
    print('批量操作执行结果（变更条数）：', response)


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


if __name__ == '__main__':
    print()
    # local_config = {
    #     'host': 'localhost',
    #     'port': '9200',
    #     'user': '',
    #     'pwd': ''
    # }
    # local_client = connect(local_config)
    #
    # index_body = """{"mappings":{"index":{"properties":{"abstract":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":1024}},"analyzer":"ccr_jieba_index","fielddata":true},"admire_cnt":{"type":"integer"},"area":{"type":"nested","properties":{"city":{"type":"keyword"},"city_code":{"type":"keyword"},"county":{"type":"keyword"},"county_code":{"type":"keyword"},"province":{"type":"keyword"},"province_code":{"type":"keyword"},"street":{"type":"keyword"},"street_code":{"type":"keyword"}}},"article_list_id":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"author":{"type":"text"},"categories":{"type":"nested","properties":{"id":{"type":"keyword"},"name":{"type":"keyword"}}},"comment_cnt":{"type":"integer"},"comments_count":{"type":"long"},"content":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":1024}},"analyzer":"ccr_jieba_index","fielddata":true},"crawl_from":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"createTime":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"created_date":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"digg_count":{"type":"long"},"distinct_id":{"type":"long"},"editor":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"enterprise_name":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"follower_count":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"id":{"type":"long"},"image_url":{"type":"keyword"},"images":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"img_list":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"impression_count":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"is_repost":{"type":"integer"},"isreprinted":{"type":"boolean"},"key_words":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"pics_url":{"type":"keyword"},"platform":{"type":"integer"},"product_names":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}},"analyzer":"ccr_jieba_index"},"products":{"properties":{"category":{"properties":{"id":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"name":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}}}},"name":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}}}},"pub_time":{"type":"date","format":"yyyy-MM-dd||yyyy-MM-dd HH:mm:ss||epoch_millis"},"read_cnt":{"type":"integer"},"repost_count":{"type":"long"},"reposts_cnt":{"type":"integer"},"reposts_count":{"type":"long"},"reposts_from":{"type":"text"},"reposts_id":{"type":"text"},"reprinted_id":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"source":{"type":"keyword"},"source_url":{"type":"keyword"},"tag":{"type":"text"},"tags":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"title":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":1024}},"analyzer":"ccr_jieba_index","fielddata":true},"video_url":{"type":"keyword"}}}},"settings":{"index":{"number_of_shards":"3","max_result_window":"1000000","analysis":{"filter":{"jieba_synonym":{"type":"synonym","synonyms_path":"jieba/synonyms.txt"},"jieba_stop":{"type":"stop","stopwords_path":"jieba/stopwords.txt"}},"analyzer":{"ccr_jieba_search":{"filter":["jieba_stop","jieba_synonym"],"tokenizer":"jieba_search"},"ccr_jieba_index":{"filter":["trim","jieba_stop"],"char_filter":["html_strip"],"tokenizer":"jieba_index"}}},"number_of_replicas":"1"}}}"""
    # index_name = 'comparative_test_detail'
    # created_index = create_index(test_client, index_name, index_body)
    #
    # re_index(prod_client, 'comparative_test_detail_20211220', test_client, created_index)
