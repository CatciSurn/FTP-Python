# _*_ coding: utf-8 _*_
import os
import sys
import socket

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
# 下载的文件存放路径
down_filepath = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'download')
# 上传的文件存放路径
upload_filepath = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'upload')
# 绑定的IP地址
BIND_HOST = '127.0.0.1'
# 绑定的端口号
BIND_PORT = 9999
ip_port = (BIND_HOST, BIND_PORT)
address_family = socket.AF_INET
socket_type = socket.SOCK_STREAM

coding = 'utf-8'
listen_count = 5
max_recv_bytes = 8192
allow_reuser_address = False
