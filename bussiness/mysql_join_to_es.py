# -*- coding: utf-8 -*-

import excel_api
import mysql_api
import es_api
from tqdm import tqdm


def convert_category(items):
    print('convert category')
    result = []
    for item in tqdm(items):
        category_name = item['审核结果(分类名称)']
        category_id = item['分类ID']
        snapshot_id = item['id']

        if category_name is not None and category_id is not None:
            category_name_arr = str(category_name).split(';')
            category_id_arr = str(category_id).split(';')

            categories = []
            for i in range(len(category_name_arr)):
                categories_item = {'name': category_name_arr[i], 'id': category_id_arr[i]}
                categories.append(categories_item)

            result_item = {'snapshot_id': snapshot_id, 'categories': categories}
            result.append(result_item)
    return result


def join(items1, items2, key):
    print('join')
    result = []
    for item1 in items1:
        for item2 in items2:
            if int(item1[key]) == int(item2[key]):
                result_item = {'id': item1['id'],
                               'categories': item2['categories']}
                result.append(result_item)
    return result


def fill_category(items1, items2, key):
    print('es fill category')
    result = []
    for item1 in tqdm(items1):
        find = False
        for item2 in items2:
            if int(item1[key]) == int(item2[key]):
                find = True
                copy_item1 = dict(item1).copy()
                copy_item1['categories'] = item2['categories']
                result.append(copy_item1)
        if bool(1 - find):
            result.append(item1)
    return result


def get_snapshot_ids(items):
    print('get_snapshot_ids')
    result = ''
    for item in tqdm(items):
        snapshot_id = item['snapshot_id']
        result += snapshot_id + ','
    return result[0:-1]


excel_config = {
    'file_path': 'D:\\1.xlsx',
    'sheet': ''
}

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'db2019'
}

es_config = {
    'host': 'localhost',
    'port': '9200',
    'user': '',
    'pwd': ''
}

if __name__ == '__main__':
    excel_data = excel_api.read_as_json(excel_config)
    excel_data = convert_category(excel_data)

    snapshot_ids = get_snapshot_ids(excel_data)

    sql = """
    SELECT
    sal.id AS id,
    sal.snapshot_id AS snapshot_id
    FROM spider_article_list sal
    LEFT JOIN cg_inspection_snap cis ON sal.snapshot_id = cis.id
    WHERE sal.snapshot_id in (%s)
    """ % (snapshot_ids)

    print("sql -> " + sql)
    fields = ['id', 'snapshot_id']
    mysql_data = mysql_api.read_as_json(mysql_config, sql, fields)

    join_data = join(mysql_data, excel_data, 'snapshot_id')

    es_client = es_api.connect(es_config)
    query_body = {"query": {"match_all": {}}, "size": 500}
    es_data = es_api.scroll_read(es_client, 'comparative_test_detail_20211220', 'index', query_body)

    fill_category_data = fill_category(es_data, join_data, 'id')

    # 创建新索引
    index_body = """{"mappings":{"index":{"properties":{"abstract":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":1024}},"analyzer":"ccr_jieba_index","fielddata":true},"admire_cnt":{"type":"integer"},"area":{"type":"nested","properties":{"city":{"type":"keyword"},"city_code":{"type":"keyword"},"county":{"type":"keyword"},"county_code":{"type":"keyword"},"province":{"type":"keyword"},"province_code":{"type":"keyword"},"street":{"type":"keyword"},"street_code":{"type":"keyword"}}},"article_list_id":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"author":{"type":"text"},"categories":{"type":"nested","properties":{"id":{"type":"keyword"},"name":{"type":"keyword"}}},"comment_cnt":{"type":"integer"},"comments_count":{"type":"long"},"content":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":1024}},"analyzer":"ccr_jieba_index","fielddata":true},"crawl_from":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"createTime":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"created_date":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"digg_count":{"type":"long"},"distinct_id":{"type":"long"},"editor":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"enterprise_name":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"follower_count":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"id":{"type":"long"},"image_url":{"type":"keyword"},"images":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"img_list":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"impression_count":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"is_repost":{"type":"integer"},"isreprinted":{"type":"boolean"},"key_words":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"pics_url":{"type":"keyword"},"platform":{"type":"integer"},"product_names":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}},"analyzer":"ccr_jieba_index"},"products":{"properties":{"category":{"properties":{"id":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"name":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}}}},"name":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}}}},"pub_time":{"type":"date","format":"yyyy-MM-dd||yyyy-MM-dd HH:mm:ss||epoch_millis"},"read_cnt":{"type":"integer"},"repost_count":{"type":"long"},"reposts_cnt":{"type":"integer"},"reposts_count":{"type":"long"},"reposts_from":{"type":"text"},"reposts_id":{"type":"text"},"reprinted_id":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"source":{"type":"keyword"},"source_url":{"type":"keyword"},"tag":{"type":"text"},"tags":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"title":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":1024}},"analyzer":"ccr_jieba_index","fielddata":true},"video_url":{"type":"keyword"}}}},"settings":{"index":{"number_of_shards":"3","max_result_window":"1000000","analysis":{"filter":{"jieba_synonym":{"type":"synonym","synonyms_path":"jieba/synonyms.txt"},"jieba_stop":{"type":"stop","stopwords_path":"jieba/stopwords.txt"}},"analyzer":{"ccr_jieba_search":{"filter":["jieba_stop","jieba_synonym"],"tokenizer":"jieba_search"},"ccr_jieba_index":{"filter":["trim","jieba_stop"],"char_filter":["html_strip"],"tokenizer":"jieba_index"}}},"number_of_replicas":"1"}}}"""
    index_name = 'comparative_test_detail'
    created_index = es_api.create_index(es_client, index_name, index_body)

    # 写入新索引
    es_api.bulk_insert(es_client, created_index, 'index', fill_category_data)
