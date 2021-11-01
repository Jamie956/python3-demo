from elasticsearch import Elasticsearch
from openpyxl import Workbook
import os
from sys import argv

'''
python .\esToExcel.py
'''

index = 'test-index'
doc = '_doc'
search_body = '{"query":{"match_all":{}}}'

es = Elasticsearch()
wb = Workbook()
ws = wb.active

# 获取文档的全部字段
mapping = es.indices.get_mapping(index)
mapping_properties = mapping[index]["mappings"][doc]["properties"]
fields = set()
for mapping_property in mapping_properties:
    fields.add(mapping_property)

# 字段header 写到excel 第一行
for i,field in enumerate(fields):
    ws.cell(1, i+1, field)

# 查询es，写到excel cell
res = es.search(index=index, doc_type=doc, body=search_body)
for i,hit in enumerate(res['hits']['hits']):
    for j,field in enumerate(fields):
        ws.cell(i+2, j+1, hit["_source"][field])

# 创建输出目录
output_dir = './output'
ouputExist = os.path.exists(output_dir)
if bool(1-ouputExist):
    print('文件夹不存在, 创建输出目录 ./output')
    os.mkdir(output_dir)

# 保存excel
wb.save(output_dir + "/esData.xlsx")