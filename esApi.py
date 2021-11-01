from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()
# es = Elasticsearch(['192.168.1.x'],http_auth=('user', 'password'),port=9200)

# 新增数据
doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime.now(),
}
res = es.index(index="test-index", id=1, body=doc)
res = es.index(index="test-index", id=2, body=doc)
print(res['result'])

# id查询
res = es.get(index="test-index", id=1)
print('_source=', res['_source'])

# 刷新
es.indices.refresh(index="test-index")

# query 查询
search_body = '{"query":{"match_all":{}}}'
res = es.search(index="test-index", doc_type="_doc", body=search_body)
for hit in res['hits']['hits']:
    print("his=", hit["_source"])
    print()
