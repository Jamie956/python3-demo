# -*- coding: utf-8 -*-
import openpyxl
from datetime import datetime


def simple_read(config):
    # 读excel
    wb = openpyxl.load_workbook(config['file_path'])
    # 选择指定sheet
    # ws = wb['gov_Information']

    ws = wb.active
    rows = tuple(ws.rows)

    for row in rows:
        row_value = ''
        for cell in row:
            row_value += str(cell.value) + ' '
        print(row_value)


def iter_read(config):
    wb = openpyxl.load_workbook(config['file_path'])
    ws = wb.active

    '''
    min_col=4: 从第4列开始读
    min_row=2: 从第二行开始读
    max_row=2: 读到第二行结束
    '''
    row_datas = []
    for datas in ws.iter_rows(min_row=2, min_col=4, max_row=2):  # 只读取第二行
        for i in range(len(datas)):
            value = datas[i].value
            row_datas.append(value)

    print(row_datas)


def iter_read2(config):
    wb = openpyxl.load_workbook(config['file_path'])
    ws = wb.active
    '''
    min_row=3：从第三行开始读
    min_col=1：从第一列开始读
    max_col=1：读到第一列结束
    '''
    col_datas = []
    for datas in ws.iter_rows(min_row=3, min_col=1, max_col=1):
        for i in range(len(datas)):
            value = datas[i].value
            col_datas.append(value)

    print(col_datas)


def write_api(config):
    wb = openpyxl.Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = 42

    # Rows can also be appended
    ws.append([1, 2, 3])

    # Python types will automatically be converted
    ws['A2'] = datetime.now()

    ws.cell(3, 1, 'insert31')
    ws.cell(3, 2, 'insert32')

    # Save the file
    wb.save(config['file_path'])


def read_as_json(config):
    print('read excel')
    wb = openpyxl.load_workbook(config['file_path'])
    ws = wb.active

    headers = []
    for items in ws.iter_rows(min_row=1, max_row=1):
        for i in range(len(items)):
            value = items[i].value
            headers.append(value)

    data = []
    for items in ws.iter_rows(min_row=2):
        row = {}
        for i in range(len(headers)):
            header = headers[i]
            value = items[i].value
            row[header] = value
        data.append(row)
    return tuple(data)


if __name__ == '__main__':
    config = {
        'file_path': './output/target.xlsx',
        'sheet': ''
    }
    print(read_as_json(config))
