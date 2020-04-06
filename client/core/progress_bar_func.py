# _*_ coding: utf-8 _*_
'''进度条的表示功能'''
import sys


def progress_bar(num, get_size, file_size):
    float_rate = float(get_size) / float(file_size)
    rate_num = round(float_rate * 100, 2)
    if num == 1:  # 1表示下载
        sys.stdout.write(
            '\033[31;1m\rfinish downloaded perentage：{0}%\033[0m'.format(rate_num))
    elif num == 2:  # 2表示上传
        sys.stdout.write(
            '\033[31;1m\rfinish uploaded perentage：{0}%\033[0m'.format(rate_num))
    sys.stdout.flush()
