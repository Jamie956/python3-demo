# -*- coding: utf-8 -*-

import time

if __name__ == '__main__':
    # # 当前时间
    # print(time.time())
    # # 时间戳形式
    # print(time.localtime(time.time()))
    # # 简单可读形式
    # print(time.asctime(time.localtime(time.time())))

    # 格式化成2019-05-07 14:17:55形式
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # # 格式化成Tue May  7 14:17:30 2019形式
    # print(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()))
    # # 将格式字符串转换为时间戳
    # a = "Tue May  7 14:17:30 2019"
    # print(time.mktime(time.strptime(a, "%a %b %d %H:%M:%S %Y")))