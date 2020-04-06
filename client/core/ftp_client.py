# _*_ coding: utf-8 _*_
import socket
import struct
import json
import os
import sys
import pickle
import hashlib

from config import settings
from core.md5_func import Md5_func
from core.file_func import File_func
from core import progress_bar_func


class FTPClient:

    def __init__(self, server_address, connect=True):
        self.server_address = server_address
        self.socket = socket.socket(
            settings.address_family, settings.socket_type)
        if connect:
            try:
                self.client_connect()
            except Exception:
                self.client_close()

    def client_connect(self):
        try:
            self.socket.connect(self.server_address)
        except Exception as e:
            print("\033[31;1merror:%s\033[0m" % e)
            exit("\033[31;1m\nThe server is not activated \033[0m")

    def client_close(self):
        self.socket.close()

    def get(self, cmds):
        """从server下载文件到client
        """
        if len(cmds) > 1:
            filename = cmds[1]
            self.file_path = os.path.join(settings.down_filepath, filename)
            if os.path.isfile(self.file_path):  # 如果文件存在，支持断电续传
                temp_file_size = os.path.getsize(self.file_path)
                self.socket.send(struct.pack('i', temp_file_size))
                header_size = struct.unpack('i', self.socket.recv(4))[0]
                if header_size:
                    filename, file_size, filemd5 = File_func(
                    ).recv_file_header(self.socket, header_size)
                    if temp_file_size == file_size:
                        print('\033[34;1mFile already does exist\033[0m')
                    else:
                        print(
                            '\033[34;1mFile now is breakpoint continuation\033[0m')
                        File_func().appendfile_content(self.socket, self.file_path, temp_file_size, file_size)
                        Md5_func().verification_filemd5(self.file_path, filemd5)
                else:
                    print(
                        "\033[34;1mFile was downloaded before,but now server's file is not exist\033[0m")
            else:  # 如果文件不存在，则是直接下载
                self.socket.send(struct.pack('i', 0))
                obj = self.socket.recv(1024)
                header_size = struct.unpack('i', obj)[0]
                if header_size == 0:
                    print("\033[31;1mfile does not exist!\033[0m")
                else:
                    filename, file_size, filemd5 = File_func(
                    ).recv_file_header(self.socket, header_size)
                    download_filepath = os.path.join(
                        settings.down_filepath, filename)
                    with open(download_filepath, 'wb') as f:
                        get_size = 0
                        File_func().write_file(self.socket, f, get_size, file_size)
                    Md5_func().verification_filemd5(self.file_path, filemd5)
        else:
            print("\033[31;1muser does not enter file name\033[0m")

    def ls(self, cmds):
        '''查看当前工作目录，文件列表'''
        print("\033[34;1mview current working directory\033[0m")
        obj = self.socket.recv(4)
        dir_size = struct.unpack('i', obj)[0]
        recv_size = 0
        recv_bytes = b''
        while recv_size < dir_size:
            temp_bytes = self.socket.recv(settings.max_recv_bytes)
            recv_bytes += temp_bytes
            recv_size += len(temp_bytes)
        print(recv_bytes.decode('gbk'))
        print('\033[31;1mCongratulations view directory success\033[0m')

    def mkdir(self, cmds):
        '''增加目录
        1，server返回1 增加成功
        2，server返回2 增加失败'''
        print("\033[34;1madd working directory\033[0m")
        obj = self.socket.recv(4)
        res = struct.unpack('i', obj)[0]
        if res:
            print('\033[31;1mCongratulations add directory success\033[0m')
        else:
            print('\033[31;1mSorry add directory failed\033[0m')

    def cd(self, cmds):
        '''切换目录'''
        print("\033[34;1mSwitch working directory\033[0m")
        if len(cmds) > 1:
            obj = self.socket.recv(4)
            res = struct.unpack('i', obj)[0]
            if res:
                print(
                    '\033[31;1mCongratulations switch directory success\033[0m')
            else:
                print('\033[31;1mSorry switch directory failed\033[0m')
        else:
            print("\033[31;1muser does not enter file name\033[0m")

    def remove(self, cmds):
        '''表示删除文件或空文件夹'''
        print("\033[34;1mRemove working directory\033[0m")
        obj = self.socket.recv(4)
        res = struct.unpack('i', obj)[0]
        if res:
            print('\033[31;1mCongratulations remove success\033[0m')
        else:
            print('\033[31;1mSorry remove directory failed\033[0m')

    def put_situation(self, file_size, condition=0):
        '''上传的时候有两种情况，文件已经存在，文件不存在'''
        quota_state = struct.unpack('i', self.socket.recv(4))[0]
        if quota_state:
            if condition:
                obj = self.socket.recv(4)
                recv_size = struct.unpack('i', obj)[0]
                File_func().open_sendfile(file_size, self.file_path, self.socket, recv_size=0)
            else:
                File_func().open_sendfile(file_size, self.file_path, self.socket, recv_size=0)
        else:
            print('\033[31;1mSorry exceeding user quotas\033[0m')

    def put(self, cmds):
        """往server端登录的用户目录下上传文件
        """
        if len(cmds) > 1:
            filename = cmds[1]
            file_path = os.path.join(settings.upload_filepath, filename)
            if os.path.isfile(file_path):  # 如果文件存在，支持断电续传
                self.socket.send(struct.pack('i', 1))
                self.file_path = file_path
                file_size = os.path.getsize(self.file_path)
                header_dic = {
                    'filename': os.path.basename(filename),
                    'file_md5':  Md5_func().getfile_md5(self.file_path),
                    'file_size': file_size
                }
                header_bytes = pickle.dumps(header_dic)
                self.socket.send(struct.pack('i', len(header_bytes)))
                self.socket.send(header_bytes)
                state = struct.unpack('i', self.socket.recv(4))[0]
                if state:  # 已经存在
                    has_state = struct.unpack('i', self.socket.recv(4))[0]
                    if has_state:
                        self.put_situation(file_size, 1)
                    else:  # 存在的大小 和文件大小一致 不必再传
                        print("\033[31;1mfile already does exist!\033[0m")
                else:  # 第一次传
                    self.put_situation(file_size)
            else:  # 文件不存在
                print("\033[31;1mfile does not exist!\033[0m")
                self.socket.send(struct.pack('i', 0))
        else:
            print("\033[31;1muser does not enter file name\033[0m")

    def get_recv(self):
        '''从client端接受发来的数据'''
        return pickle.loads(self.socket.recv(settings.max_recv_bytes))

    def login(self):
        '''
        登陆函数，当登陆失败超过三次，则退出
        用户密码发送到server短
        接受server端返回的信息，如果成功返回1，失败返回0
        :return: 如果用户账号密码正确，则返回用户数据的字典
        '''
        retry_count = 0
        while retry_count < 3:
            username = input('\033[34;1mplease input Username:\033[0m').strip()
            if not username:
                continue
            password = input('\033[34;1mplease input Password:\033[0m').strip()
            user_dic = {
                'username': username,
                'password': password
            }
            # 将用户信息发送到客户端，然后接受客户端的数据
            data = pickle.dumps(user_dic)
            self.socket.send(pickle.dumps(user_dic))
            # 为了防止出现黏包问题，所以先解压报头，读取报头，再读数据
            obj = self.socket.recv(4)
            res = struct.unpack('i', obj)[0]
            # 此处，如果返回的是代码4001，则成功 4002则失败
            if res:
                print(
                    "\033[32;1m-----------------welcome to ftp client-------------------\033[0m")
                user_info_dic = self.get_recv()
                recv_username = user_info_dic['username']
                return True
            else:
                print("\033[31;1mAccount or Passwordoes not correct!\033[0m")
        retry_count += 1

    def execute(self):
        '''
        执行，或者实施
        :return:
        '''
        if self.login():
            while True:
                try:
                    self.help_info()
                    inp = input("Please input a command>>>").strip()
                    if not inp:
                        continue
                    self.socket.send(inp.encode(settings.coding))
                    cmds = inp.split()
                    if hasattr(self, cmds[0]):
                        func = getattr(self, cmds[0])
                        func(cmds)
                        break
                    else:
                        print(
                            '\033[31;1mNo such command ,please try again\033[0m')
                except Exception as e:  # server关闭了
                    print('\033[31;1m%s\033[0m' % e)
                    break

    def help_info(self):
        print('''\033[34;1m
              get + (文件名）    表示下载文件
              put + (文件名）    表示上传文件
              ls                 表示查询当前目录下的文件列表（只能访问自己的文件列表） 
              mkdir + (文件名）  表示创建文件夹  
              cd + (文件名）     表示切换目录（只能在自己的文件列表中切换）
              remove + (文件名） 表示删除文件或空文件夹
        \033[0m''')
