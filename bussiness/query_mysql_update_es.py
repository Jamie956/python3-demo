
import pymysql_api
import es_util

if __name__ == '__main__':
    mysql_config = {
        'host': '192.168.1.*',
        'user': '*',
        'password': '*',
        'database': '*'
    }
    es_config = {
        'host': '',
        'port': '',
        'user': '',
        'pwd': ''
    }

    mysql_client = pymysql_api.get_client(mysql_config)
    sql = "SELECT id, snapshot_id FROM cg_recall_detail"
    mysql_result = pymysql_api.query_raw_data(mysql_client, sql)
    id_map = {}
    for row in mysql_result:
        id_map[row[0]] = row[1]

    es_client = es_util.get_client(es_config)
    es_result = es_util.scroll_read(es_client, "recall_detail_211", "index", {"query": {"match_all": {}}})

    for e in es_result:
        e['snapshot_id'] = id_map[e['id']]

    es_util.bulk_update(es_client,  "recall_detail_211", "index", es_result, 'snapshot_id')


