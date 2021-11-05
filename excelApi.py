# -*- coding: utf-8 -*-
import openpyxl
import sys
from datetime import datetime
import os


def simple_read():
    # 读excel
    wb = openpyxl.load_workbook('./output/target.xlsx')

    # 选择指定sheet
    # ws = wb['gov_Information']

    ws = wb.active
    rows = tuple(ws.rows)

    for row in rows:
        row_value = ''
        for cell in row:
            row_value += str(cell.value) + ' '
        print(row_value)


# 插入大量测试数据
def init_scroll_data():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(
        ["column1", "column2", "column3", "column4", "column5", "column6", "column7", "column8", "column9", "column10",
         "column11"])
    for i in range(10000):
        ws.append([i, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0])
    wb.save("./output/target.xlsx")


def scroll_read():
    start = datetime.now()
    # 耗时（秒） 0.844773，read_only=False
    # wb = openpyxl.load_workbook('./output/target.xlsx',read_only=False)
    # 耗时（秒） 0.528589，read_only=True
    wb = openpyxl.load_workbook('./output/target.xlsx', read_only=True)
    # 结论：read_only=True 可以加快读取速度
    ws = wb.active

    # rows = tuple(ws.rows)
    # print(sys.getsizeof(rows) / 1024 / 1024, 'MB')
    # 1000 - 0.0076751708984375 MB
    # 10000 - 0.0763397216796875 MB
    # 结论：一次加载全部rows到内存

    # excel 有10000 行数据，读100行，占用内存 0.00011444091796875 MB
    # print(sys.getsizeof(ws.iter_rows(min_row=1, min_col=1, max_row=100)) / 1024 / 1024, 'MB')
    # excel 有10000 行数据，读5000行，占用内存 0.00011444091796875 MB
    # print(sys.getsizeof(ws.iter_rows(min_row=1, min_col=1, max_row=5000)) / 1024 / 1024, 'MB')
    # excel 有10000 行数据，读全部行，占用内存 0.00011444091796875 MB
    # print(sys.getsizeof(ws.rows) / 1024 / 1024, 'MB')
    # 结论：iter_rows和rows 没有真实读取数据

    # 读取真实数据 0.7629852294921875 MB
    # print(sys.getsizeof(tuple(ws.rows)) / 1024 / 1024, 'MB')

    '''
    min_col=4: 从第4列开始读
    min_row=2: 从第二行开始读
    max_row=2: 读到第二行结束
    '''
    # row_datas = []
    # for datas in ws.iter_rows(min_row=2, min_col=4, max_row=2):  # 只读取第二行
    #     for i in range(len(datas)):
    #         value = datas[i].value
    #         row_datas.append(value)

    '''
    min_row=3：从第三行开始读
    min_col=1：从第一列开始读
    max_col=1：读到第一列结束
    '''
    # col_datas = []
    # for datas in ws.iter_rows(min_row=3, min_col=1, max_col=1):
    #     for i in range(len(datas)):
    #         value = datas[i].value
    #         col_datas.append(value)

    # 读取起始行
    start_row = 2
    # 每批数据的大小
    batch_size = 100
    # todo 循环直至全部数据读取完

    json_list = []
    for row in ws.iter_rows(min_row=start_row, max_row=batch_size):
        values = tuple(cell.value for cell in row)
        # todo 与 第一行 header 组成一个json，放入list
    # todo 将json_list 批量插入到es
    print('耗时（秒）', (datetime.now() - start).microseconds / 1000000)


def write_api():
    wb = openpyxl.Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = 42

    # Rows can also be appended
    # 插入下一行
    ws.append([1, 2, 3])

    # Python types will automatically be converted
    ws['A2'] = datetime.now()

    ws.cell(3, 1, '111')
    ws.cell(3, 2, '222')

    # 如果不存在，创建output 文件夹
    ouputExist = os.path.exists('./output')
    if bool(1 - ouputExist):
        print('文件夹不存在, 创建输出目录 ./output')
        os.mkdir('./output')

    # Save the file
    wb.save("./output/target.xlsx")


if __name__ == '__main__':
    # simple_read()
    init_scroll_data()
    scroll_read()
    # write_api()
    print()
