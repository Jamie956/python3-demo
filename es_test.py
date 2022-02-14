# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import math
import time


# 连接
def get_client(config):
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

def exist(client):
    return client.exists(index="public_opinion", doc_type="index", id="1454602904190328832")

if __name__ == '__main__':
    cf = {
        'host': '',
        'port': '',
        'user': '',
        'pwd': ''
    }
    client = get_client(cf)

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
