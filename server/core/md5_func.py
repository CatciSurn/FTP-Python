# _*_ coding: utf-8 _*_
import hashlib
import struct

from core import ftp_server
from core import file_func


class Md5_func(object):

    def getfile_md5(self, file_path):
        '''获取文件的md5'''
        md5 = hashlib.md5(file_func.File_func().readfile(file_path))
        print("md5是：\n", md5.hexdigest())
        return md5.hexdigest()

    def handle_data(self):
        '''处理接收到的数据，主要是将密码转化为md5的形式'''
        user_dic = ftp_server.FTPServer().get_recv()
        username = user_dic['username']
        password = user_dic['password']
        md5_obj = hashlib.md5()
        md5_obj.update(password)
        check_password = md5_obj.hexdigest()

    def verification_filemd5(self, file_path, conn, filemd5):
        # 判断文件内容的md5
        if self.getfile_md5(file_path) == filemd5:
            print('\033[31;1mCongratulations download success\033[0m')
            conn.send(struct.pack('i', 1))
        else:
            print('\033[31;1mSorry download failed\033[0m')
            conn.send(struct.pack('i', 0))
