# -*- coding: utf-8 -*-

def print_func(par):
    print("Hello : ", par)
    return


a = 1
print(dir())

# 每个模块都有一个__name__属性，当其值是'__main__'时，表明该模块自身在运行
if __name__ == '__main__':
    print('程序自身运行')
else:
    print('另一模块调起')
