# _*_ coding: utf-8 _*_
import pickle
import hashlib
import os
import struct

from config import settings
from core.user_handle import UserHandle
from core.file_func import File_func


class Auth_func():

    def auth(self, conn):
        '''
        处理用户的认证请求
        1，根据username读取accounts.ini文件，然后查看用户是否存在
        2，将程序运行的目录从bin.user_auth修改到用户home/username方便之后查询
        3，把客户端返回用户的详细信息
        :return:
        '''
        while True:
            user_dic = self.get_recv(conn)
            username = user_dic['username']
            password = user_dic['password']
            md5_obj = hashlib.md5(password.encode('utf-8'))
            check_password = md5_obj.hexdigest()
            user_handle = UserHandle(username)
            # 判断用户是否存在 返回列表,
            user_data = user_handle.judge_user()
            if user_data:
                if user_data[0][1] == check_password:
                    conn.send(struct.pack('i', 1))  # 登录成功返回 1
                    self.homedir_path = os.path.join(
                        settings.BASE_DIR, 'home', username)
                    # 将程序运行的目录名修改到 用户home目录下
                    os.chdir(self.homedir_path)
                    # 将用户配额的大小从M 改到字节
                    self.quota_bytes = int(user_data[2][1]) * 1024 * 1024
                    user_info_dic = {
                        'username': username,
                        'homedir': user_data[1][1],
                        'quota': user_data[2][1]
                    }
                    # 用户的详细信息发送到客户端
                    conn.send(pickle.dumps(user_info_dic))
                    return True
                else:
                    conn.send(struct.pack('i', 0))  # 登录失败返回 0
            else:
                conn.send(struct.pack('i', 0))  # 登录失败返回 0

    def get_recv(self, conn):
        '''从client端接收发来的数据'''
        return pickle.loads(conn.recv(settings.max_recv_bytes))

    def current_home_size(self):
        """得到当前用户目录的大小，字节/M"""
        self.home_bytes_size = 0
        File_func().recursion_file(self.homedir_path, self.home_bytes_size)
        home_m_size = round(self.home_bytes_size / 1024 / 1024, 1)
