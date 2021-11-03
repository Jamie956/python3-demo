# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from openpyxl import Workbook

# 需求：读取excel 把数据更新到es

# 分批读取excel 数据，每批数据使用 es bulk插入es