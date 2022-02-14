import excel_api
import es_util
import json


def arr_str_to_json(arr_str):
    convert_arr_str = str(arr_str).replace("\'", '"')
    return json.loads(convert_arr_str)


if __name__ == '__main__':
    es_cf = {
        'host': '',
        'port': '',
        'user': '',
        'pwd': ''
    }
    es_client = es_util.get_client(es_cf)
    index = "public_opinion"

    data = excel_api.read_as_json('D:/projectb/python3-demo/bussiness/output/aaa.xlsx')

    for e in data:
        id = e['id']
        print(id)
        doc = {
            'abstract': e['abstract'],
            'area': arr_str_to_json(e['area']),
            'categories': arr_str_to_json(e['categories']),
            'product_names': arr_str_to_json(e['product_names']),
            'tags': arr_str_to_json(e['tags'])
        }

        # if es_util.exist(es_client, index, id) is False:
        #     print('文档不存在，id='+id)
        es_util.update_by_id(es_client, index, id, doc)
