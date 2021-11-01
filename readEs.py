from datetime import datetime
from elasticsearch import Elasticsearch
# es = Elasticsearch()
es = Elasticsearch(['192.168.1.201'],http_auth=('elastic', '123456'),port=9200)

# 新增数据
# doc = {
#     'author': 'kimchy',
#     'text': 'Elasticsearch: cool. bonsai cool.',
#     'timestamp': datetime.now(),
# }
# res = es.index(index="test-index", id=1, body=doc)
# print(res['result'])

# id查询
# res = es.get(index="test-index", id=1)
# print('_source=', res['_source'])

# 刷新
# es.indices.refresh(index="test-index")

# query 查询
search_body = '{"query":{"bool":{"filter":[{"bool":{"must":[{"term":{"tags.keyword":{"value":"初筛"}}},{"term":{"tags.keyword":{"value":"事件"}}},{"bool":{"should":[{"term":{"tags.keyword":{"value":"致伤病"}}},{"term":{"tags.keyword":{"value":"致财产损失"}}},{"term":{"tags.keyword":{"value":"产品导致伤害"}}}]}},{"nested":{"query":{"exists":{"field":"categories"}},"path":"categories"}}]}}]}}}'
res = es.search(index="public_opinion", doc_type="index", body=search_body)
for hit in res['hits']['hits']:
    print("his=", hit["_source"])
    print()
