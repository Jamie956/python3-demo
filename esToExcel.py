# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from openpyxl import Workbook
import os
from datetime import datetime
import re

index = 'test_index'
doc = '_doc'
search_body = {"query":{"match_all":{}},"size":100}
es = Elasticsearch()

wb = Workbook()
ws = wb.active
ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
start = datetime.now()

# 创建输出目录
output_dir = './output'
ouputExist = os.path.exists(output_dir)
if bool(1 - ouputExist):
    print('文件夹不存在, 创建输出目录 ./output')
    os.mkdir(output_dir)

# 获取文档的全部字段
fields = []
mapping = es.indices.get_mapping(index)
for key in mapping:
    if index in key:
        mapping_properties = mapping[key]["mappings"][doc]["properties"]
        for mapping_property in mapping_properties:
            fields.append(mapping_property)

# 字段header 写到excel 第一行
ws.append(fields)

# 查询首页，获取返回滚动id

page = es.search(body=search_body, index=index, doc_type=doc, scroll="2m")
# 滚动id
sid = page['_scroll_id']
# 查询页大小
total = page['hits']['total']
scroll_size = page['hits']['total']

# 写到excel
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
wb.save(output_dir + "/esData.xlsx")


print('首页查询', str(len(page['hits']['hits'])), '条 保存到excel', '耗时（秒）', (datetime.now() - start).microseconds / 1000000)

# 滚动写到excel
cur_size = len(page['hits']['hits'])
while (scroll_size > 0):
    scroll_start = datetime.now()
    page = es.scroll(scroll_id=sid, scroll='2m')
    sid = page['_scroll_id']
    # 命中数据条数
    scroll_size = len(page['hits']['hits'])
    # 写到excel
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
    wb.save(output_dir + "/esData.xlsx")
    cur_size += scroll_size
    print('滚动查询', str(cur_size), '/', str(total), '条 保存到excel', '耗时（秒）', (datetime.now() - scroll_start).microseconds / 1000000)

print('总耗时（秒）', (datetime.now() - start).microseconds / 1000000)
