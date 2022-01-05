# -*- coding: utf-8 -*-

import excel_api
import mysql_api
import es_api
from tqdm import tqdm

excel_api.config = {
    'file_path': 'D:\\test_category.xlsx',
    'sheet': ''
}


def convert_excel_category(items):
    print('convert category')
    result = []
    for item in tqdm(items):
        category_name = item['categoryName']
        category_id = item['categoryId']
        snapshot_id = item['snapshotId']

        if category_name is not None and category_id is not None:
            category_name_arr = str(category_name).split(';')
            category_id_arr = str(category_id).split(';')

            categories = []
            for i in range(len(category_name_arr)):
                categories_item = {'name': category_name_arr[i], 'id': category_id_arr[i]}
                categories.append(categories_item)

            result_item = {'snapshot_id': snapshot_id, 'categories': categories}
            result.append(result_item)
    return result


def join_data(items1, items2, key):
    print('mysql join excel')
    result = []
    for item1 in items1:
        for item2 in items2:
            if int(item1[key]) == int(item2[key]):
                result_item = {'id': item1['id'],
                               'categories': item2['categories']}
                result.append(result_item)
    return result


def es_fill_category(items1, items2, key):
    print('es fill category')
    result = []
    for item1 in tqdm(items1):
        find = False
        for item2 in items2:
            if int(item1[key]) == int(item2[key]):
                find = True
                copy_item1 = dict(item1).copy()
                copy_item1['categories'] = item2['categories']
                result.append(copy_item1)
        if bool(1 - find):
            result.append(item1)
    return result


'''
read mysql、excel data
mysql data join excel data
join data insert to es
'''
if __name__ == '__main__':
    sql = """
    """
    fields = ['id', 'snapshot_id']
    mysql_items = mysql_api.read_as_json(sql, fields)

    excel_items = excel_api.read_as_json()
    convert_excel_category_items = convert_excel_category(excel_items)

    mysql_fill_category_items = join_data(mysql_items,
                                          convert_excel_category_items, 'snapshot_id')

    query_body = {"query": {"match_all": {}}, "size": 500}
    es_items = es_api.scroll_read('comparative_test_detail_20211220', 'index', query_body)

    es_fill_category_items = es_fill_category(es_items,
                                              mysql_fill_category_items, 'id')

    es_api.bulk_insert('comparative_test_detail_20220105', 'index', es_fill_category_items)
