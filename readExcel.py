# -*- coding: utf-8 -*-
import openpyxl

#读excel
wb = openpyxl.load_workbook('./output/target.xlsx')

#选择指定sheet
# ws = wb['gov_Information']

ws = wb.active
rows = tuple(ws.rows)

for row in rows:
    row_value = ''
    for cell in row:
        row_value += str(cell.value)+' '
    print (row_value)
