from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()

# 新增数据
# doc = {
#     'author': 'kimchy',
#     'text': 'Elasticsearch: cool. bonsai cool.',
#     'timestamp': datetime.now(),
# }
# for i in range(1000):
#     es.index(index="test_index", body=doc)

# 查询首页，获取返回滚动id
page = es.search(body={"query":{"match_all":{}},"size":100}, index="test_index", doc_type="_doc", scroll="2m")
# 滚动id
sid = page['_scroll_id']
# 查询页大小
scroll_size = page['hits']['total']

while(scroll_size > 0):
    start = datetime.now()
    page = es.scroll(scroll_id=sid, scroll='2m')
    sid = page['_scroll_id']
    # 命中数据条数
    scroll_size = len(page['hits']['hits'])
    print('页查询',str(scroll_size),'条','消耗时间（毫秒）',(datetime.now()-start).microseconds)
