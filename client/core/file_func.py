# _*_ coding: utf-8 _*_
import os
import sys
import struct
import pickle
from config import settings
from core import ftp_client
from core import md5_func
from core import progress_bar_func


class File_func(object):

    def readfile(self, file_path):
        '''读取文件'''
        with open(file_path, 'rb') as f:
            filedata = f.read()
        return filedata

    def appendfile_content(self, socket, file_path, temp_file_size, file_size):
        '''追加文件内容'''
        with open(file_path, 'ab') as f:
            f.seek(temp_file_size)
            get_size = temp_file_size
            while get_size < file_size:
                res = socket.recv(settings.max_recv_bytes)
                f.write(res)
                get_size += len(res)
                progress_bar_func.progress_bar(1, get_size, file_size)  # 1表示下载

    def write_file(self, socket, f, get_size, file_size):
        '''下载文件，将内容写入文件中'''
        while get_size < file_size:
            res = socket.recv(settings.max_recv_bytes)
            f.write(res)
            get_size += len(res)
            progress_bar_func.progress_bar(1, get_size, file_size)  # 1表示下载

    def recv_file_header(self, socket, header_size):
        """接收文件的header, filename file_size file_md5"""
        header_types = socket.recv(header_size)
        header_dic = pickle.loads(header_types)
        print(header_dic, type(header_dic))
        total_size = header_dic['file_size']
        filename = header_dic['filename']
        filemd5 = header_dic['filemd5']
        return (filename, total_size, filemd5)

    def open_sendfile(self, file_size, file_path, socket, recv_size=0):
        '''打开要上传的文件（由于本程序上传文件的原理是先读取本地文件，再写到上传地址的文件）'''
        with open(file_path, 'rb') as f:
            f.seek(recv_size)
            while True:
                data = f.read(1024)
                if data:
                    socket.send(data)
                    obj = socket.recv(4)
                    recv_size = struct.unpack('i', obj)[0]
                    progress_bar_func.progress_bar(2, recv_size, file_size)
                else:
                    break
        success_state = struct.unpack('i', socket.recv(4))[0]
        if success_state:
            print('\033[31;1mCongratulations upload success\033[0m')
        else:
            print('\033[31;1mSorry upload directory failed\033[0m')
