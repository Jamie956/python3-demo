#-*- coding:utf-8 -*-
from sys import argv

# python .\arg_parse.py --first aaa --sec sss

dict = {}
for i,arg in enumerate(argv):
    # 是否包含'--'
    if '--' in arg:
        key = argv[i].replace('--', '')
        value = argv[i+1]
        dict[key] = value

print(dict)