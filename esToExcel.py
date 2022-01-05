# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from openpyxl import Workbook
import re
import es_api

es = Elasticsearch()

wb = Workbook()
ws = wb.active
ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')


def es_query_data(query_result, headers):
    rows = []
    for i, e in enumerate(query_result['hits']['hits']):
        row = []
        for j, header in enumerate(headers):
            doc_data = e["_source"]
            if header in doc_data.keys():
                value = str(doc_data[header])
                # 去除excel非法字符，否在抛出异常 openpyxl.utils.exceptions.IllegalCharacterError
                row.append(ILLEGAL_CHARACTERS_RE.sub(r'', value))
            else:
                # 字段不存在，写入空
                row.append('')
        rows.append(row)
    return rows


if __name__ == '__main__':
    index = 'test_index'
    doc = 'index'
    search_body = {"query": {"match_all": {}}, "size": 100}

    fields = es_api.mapping_fields(index, doc)
    # header 写到excel 第一行
    ws.append(fields)

    # 查询首页，获取返回滚动id
    page = es.search(body=search_body, index=index, doc_type=doc, scroll="2m")
    sid = page['_scroll_id']
    scroll_size = page['hits']['total']

    rows = es_query_data(page, fields)

    for row in rows:
        ws.append(row)
    wb.save("./output/esData.xlsx")

    # 滚动写到excel
    cur_size = len(page['hits']['hits'])
    while (scroll_size > 0):
        page = es.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        scroll_size = len(page['hits']['hits'])
        rows = es_query_data(page, fields)

        for row in rows:
            ws.append(row)
        wb.save("./output/esData.xlsx")
