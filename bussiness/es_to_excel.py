# -*- coding: utf-8 -*-
import es_api
import excel_api

'''
    config = {
        'es_connect': {
            'host': '192.168.1.201',
            'port': '9200',
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
    config = {
        'es_connect': {
            'host': '192.168.1.201',
            'port': '9200',
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
    scroll_read_es_write_to_excel_by_config(config)
