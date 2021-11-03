import sys
import psutil

# 获取对象占用内存

a = '0'
for i in range(102400):
    a += str(i)

print(sys.getsizeof(a), 'byte')
print(sys.getsizeof(a) / 1024 / 1024, 'MB')

info = psutil.virtual_memory()
print(u'电脑总内存：%.4f GB' % (info.total / 1024 / 1024 / 1024))
print(u'当前使用的总内存占比：', info.percent)
print(u'cpu个数：', psutil.cpu_count())
