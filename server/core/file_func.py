# _*_ coding: utf-8 _*_
import os
import sys
import struct
import pickle
 
from config import settings
from core import ftp_server
from core import md5_func
 
 
class File_func(object):
    def readfile(self,file_path):
        '''读取文件，得到文件内容的bytes类型'''
        with open(file_path, 'rb') as f:
            filedata = f.read()
        return filedata
 
    def send_filedata(self,file_path,conn,exist_file_size=0):
        """下载时，将文件打开，send(data)"""
        with open(file_path, 'rb') as f:
            f.seek(exist_file_size)
            while True:
                data = f.read(1024)
                if data:
                    conn.send(data)
                else:
                    break
 
    def write_file(self,conn,f,recv_size,file_size):
        '''上传文件时，将文件内容写入到文件中'''
        while recv_size < file_size:
            res = conn.recv(settings.max_recv_bytes)
            f.write(res)
            recv_size += len(res)
            conn.send(struct.pack('i', recv_size))  # 为了进度条的显示
 
    def recursion_file(self, homedir_path,home_bytes_size):
        """递归查询用户目录下的所有文件，算出文件的大小"""
        res = os.listdir(homedir_path)
        for i in res:
            path = os.path.join(homedir_path,i)
            if os.path.isdir(path):
                self.recursion_file(path,home_bytes_size)
            elif os.path.isfile(path):
                home_bytes_size += os.path.getsize(path)
 
    def current_home_size(self,homedir_path):
        """得到当前用户目录的大小，字节/M"""
        self.home_bytes_size =0
        self.recursion_file(self.home_bytes_size,homedir_path)
        home_m_size = round(self.home_bytes_size / 1024 / 1024, 1)