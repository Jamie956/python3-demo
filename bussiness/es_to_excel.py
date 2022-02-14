# -*- coding: utf-8 -*-
import es_test
import excel_api
import es_util

'''
    config = {
        'es_connect': {
  'host': '',
  'port': '',
  'user': '',
  'pwd': ''
        },
        'output_path': './output/20220121.xlsx',
        'data_config': [
            {
                'index': 'comparative_test',
                'type': 'index',
                'query': {"size": 400},
                'sheet': '比较试验',
                'headers': ['id', 'title', 'source_url']
            },
            {
                'index': 'public_opinion',
                'type': 'index',
                'query': {"size": 400},
                'sheet': '舆情',
                'headers': ['id', 'title']
            }
        ]
    }
'''


def scroll_read_es_write_to_excel_by_config(config):
    es_client = es_api.connect(config['es_connect'])
    output_path = config['output_path']

    write_excel_config = []
    for data_config in config['data_config']:
        query_result = es_api.scroll_read(es_client, data_config['index'], data_config['type'], data_config['query'])
        write_excel_config.append({
            'sheet': data_config['sheet'],
            'headers': data_config['headers'],
            'data': query_result
        })

    excel_api.batch_write2excel_by_config(output_path, write_excel_config)

if __name__ == '__main__':
    es_client = es_util.get_client({
            'host': '',
            'port': '',
            'user': '',
            'pwd': ''
        })

    comparative_test_fields = es_util.mapping_fields(es_client, 'comparative_test', 'index')
    complaint_fields = es_util.mapping_fields(es_client, 'complaint', 'index')

    config = {
        'es_connect': {
            'host': '',
            'port': '',
            'user': '',
            'pwd': ''
        },
        'output_path': './output/20220209-1.xlsx',
        'data_config': [
            {
                'index': 'comparative_test',
                'type': 'index',
                'query': '''{"query":{"range":{"pub_time":{"gte":"2020-06-18"}}}}''',
                'sheet': '比较试验',
                'headers': comparative_test_fields
            },
            {
                'index': 'complaint',
                'type': 'index',
                'query': '''{"query":{"range":{"pub_time":{"gte":"2022-02-08"}}}}''',
                'sheet': '投诉举报',
                'headers': complaint_fields
            }
        ]
    }
    scroll_read_es_write_to_excel_by_config(config)
