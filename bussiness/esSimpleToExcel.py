# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from openpyxl import Workbook
import os
from datetime import datetime
import re

es = Elasticsearch(['192.168.1.*'], http_auth=('**', '**'), port=9200)

wb = Workbook()
ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')


# 获取输出文件路径
def get_file_path():
    # 创建输出目录
    output_dir = './output'
    output_exist = os.path.exists(output_dir)
    if bool(1 - output_exist):
        print('文件夹不存在, 创建输出目录 ./output')
        os.mkdir(output_dir)

    return output_dir + "/es_data_export.xlsx"


# 获取文档的全部字段
def get_headers(index, doc):
    fields = []
    mapping = es.indices.get_mapping(index)
    for key in mapping:
        if index in key:
            mapping_properties = mapping[key]["mappings"][doc]["properties"]
            for mapping_property in mapping_properties:
                fields.append(mapping_property)
    return fields


# 滚动写到excel
def write_to_excel(index, doc, search_body, ws):
    file_path = get_file_path()
    fields = get_headers(index, doc)

    start = datetime.now()
    # 查询首页，获取返回滚动id
    page = es.search(body=search_body, index=index, doc_type=doc, scroll="2m")
    # 滚动id
    sid = page['_scroll_id']
    # 查询页大小
    total = page['hits']['total']
    scroll_size = page['hits']['total']

    page_data_to_excel(page, fields, ws, file_path)

    print('首页查询', str(len(page['hits']['hits'])), '条 保存到excel', '耗时（秒）',
          (datetime.now() - start).microseconds / 1000000)

    # 滚动写到excel
    cur_size = len(page['hits']['hits'])
    while scroll_size > 0:
        scroll_start = datetime.now()
        page = es.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        # 命中数据条数
        scroll_size = len(page['hits']['hits'])

        page_data_to_excel(page, fields, ws, file_path)

        cur_size += scroll_size
        print('滚动查询', str(cur_size), '/', str(total), '条 保存到excel', '耗时（秒）',
              (datetime.now() - scroll_start).microseconds / 1000000)

    print('总耗时（秒）', (datetime.now() - start).microseconds / 1000000)


def page_data_to_excel(page, fields, ws, file_path):
    for i, hit in enumerate(page['hits']['hits']):
        write_row = []
        for j, field in enumerate(fields):
            if field in hit["_source"].keys():
                field_value = str(hit["_source"][field])
                # 去除excel非法字符，否在抛出异常 openpyxl.utils.exceptions.IllegalCharacterError
                field_value = ILLEGAL_CHARACTERS_RE.sub(r'', field_value)
                write_row.append(field_value)
            else:
                # 字段不存在，写入空
                write_row.append('')
        ws.append(write_row)

    # 保存页数据到excel
    wb.save(file_path)


def entry(index):
    doc = 'index'
    search_body = {"size": 1000, "query": {
        "bool": {"filter": [{"range": {"pub_time": {"gte": "2021-06-22", "lte": "2021-11-30"}}}],
                 "should": [{"terms": {"title": ["电动自行车", "电动车"]}}, {"terms": {"content": ["电动自行车", "电动车"]}}],
                 "minimum_should_match": 1}}}

    wb.create_sheet(title=index)
    ws = wb[index]

    fields = get_headers(index, doc)
    # 字段header 写到excel 第一行
    ws.append(fields)
    write_to_excel(index, doc, search_body, ws)


if __name__ == '__main__':
    entry('public_opinion')
    entry('market')
    entry('recall')
    entry('complaint')
    entry('comparative_test')
