# _*_ coding: utf-8 _*_
import socket
import struct
import json
import os
import pickle
import subprocess
import hashlib
import queue
from threading import Thread
from threading import currentThread

from config import settings
from core.user_handle import UserHandle
from core.file_func import File_func
from core.md5_func import Md5_func
# from core.auth_func import Auth_func
from core.auth import Auth_func


class FTPServer():

    def __init__(self, server_address, bind_and_listen=True):
        self.server_address = server_address
        self.socket = socket.socket(
            settings.address_family, settings.socket_type)
        self.q = queue.Queue(settings.MAX_CONCURRENT_COUNT)
        if bind_and_listen:
            try:
                self.server_bind()
                self.server_listen()
            except Exception:
                self.server_close()

    def server_bind(self):
        allow_reuse_address = False
        if allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def server_listen(self):
        self.socket.listen(settings.listen_count)

    def server_close(self):
        self.socket.close()

    def server_accept(self):
        return self.socket.accept()

    def conn_close(self, conn):
        conn.close()

    def server_link(self):
        print("\033[31;1mwaiting client .....\033[0m")
        while True:  # 链接循环
            conn, self.client_addr = self.server_accept()
            print('客户端地址:', self.client_addr)
            # while True:  # 通信循环
            try:
                t = Thread(target=self.server_handle, args=(conn,))
                self.q.put(t)
                t.start()
            except Exception as e:
                print(e)
                self.conn_close(conn)
                self.q.get()

    def server_handle(self, conn):
        '''处理与用户的交互指令'''
        if Auth_func().auth(conn):
            print(
                "\033[32;1m-------user authentication successfully-------\033[0m")
            try:
                res = conn.recv(settings.max_recv_bytes)
                if not res:
                    self.conn_close(conn)
                    self.q.get()
                # 解析命令，提取相应的参数
                self.cmds = res.decode(settings.coding).split()
                if hasattr(self, self.cmds[0]):
                    func = getattr(self, self.cmds[0])
                    func(conn)
            except Exception as e:
                print(e)
                self.conn_close(conn)
                self.q.get()

    def get(self, conn):
        '''
       下载，首先查看文件是否存在，然后上传文件的报头大小，上传文件，以读的方式发开文件
       找到下载的文件
            发送 header_size
            发送 header_bytes file_size
            读文件 rb 发送 send(line)
            若文件不存在，发送0 client提示：文件不存在
       :param cmds:
       :return:
               '''
        if len(self.cmds) > 1:
            filename = self.cmds[1]
            self.file_path = os.path.join(os.getcwd(), filename)
            if os.path.isfile(self.file_path):
                file_size = os.path.getsize(self.file_path)
                obj = conn.recv(4)
                exist_file_size = struct.unpack('i', obj)[0]
                header = {
                    'filename': filename,
                    'filemd5': Md5_func().getfile_md5(self.file_path),
                    'file_size': file_size
                }
                header_bytes = pickle.dumps(header)
                conn.send(struct.pack('i', len(header_bytes)))
                conn.send(header_bytes)
                if exist_file_size:  # 表示之前被下载过 一部分
                    if exist_file_size != file_size:
                        File_func().send_filedata(self.file_path, exist_file_size)
                    else:
                        print(
                            '\033[31;1mbreakpoint and file size are the same\033[0m')
                else:  # 文件第一次下载
                    File_func().send_filedata(self.file_path, conn)
            else:
                print('\033[31;1merror\033[0m')
                conn.send(struct.pack('i', 0))

        else:
            print("\033[31;1muser does not enter file name\033[0m")

    def put(self, conn):
        """从client上传文件到server当前工作目录下
        """
        if len(self.cmds) > 1:
            obj = conn.recv(4)
            state_size = struct.unpack('i', obj)[0]
            if state_size:
                # 算出了home下已被占用的大小self.home_bytes_size
                self.current_home_size()
                header_bytes = conn.recv(struct.unpack('i', conn.recv(4))[0])
                header_dic = pickle.loads(header_bytes)
                filename = header_dic.get('filename')
                file_size = header_dic.get('file_size')
                file_md5 = header_dic.get('file_md5')
                self.file_path = os.path.join(os.getcwd(), filename)
                if os.path.exists(self.file_path):
                    conn.send(struct.pack('i', 1))
                    has_size = os.path.getsize(self.file_path)
                    if has_size == file_size:
                        print("\033[31;1mfile already does exist!\033[0m")
                        conn.send(struct.pack('i', 0))
                    else:
                        print(
                            '\033[31;1mLast time  file not finished,this time continue\033[0m')
                        conn.send(struct.pack('i', 1))
                        if self.home_bytes_size + int(file_size - has_size) > self.quota_bytes:
                            print(
                                '\033[31;1mSorry exceeding user quotas\033[0m')
                            conn.send(struct.pack('i', 0))
                        else:
                            conn.send(struct.pack('i', 1))
                            conn.send(struct.pack('i', has_size))
                            with open(self.file_path, 'ab') as f:
                                f.seek(has_size)
                                File_func().write_file(conn, f, has_size, file_size)
                            Md5_func().verification_filemd5(self.file_path, conn, file_md5)

                else:
                    conn.send(struct.pack('i', 0))
                    print('\033[31;1mfile does not exist, now first put\033[0m')
                    if self.home_bytes_size + int(file_size) > self.quota_bytes:
                        print('\033[31;1mSorry exceeding user quotas\033[0m')
                        conn.send(struct.pack('i', 0))
                    else:
                        conn.send(struct.pack('i', 1))
                        with open(self.file_path, 'wb') as f:
                            recv_size = 0
                            File_func().write_file(conn, f, recv_size, file_size)
                        Md5_func().verification_filemd5(self.file_path, conn, file_md5)

            else:
                print("\033[31;1mfile does not exist!\033[0m")
        else:
            print("\033[31;1muser does not enter file name\033[0m")

    def ls(self, conn):
        '''查看当前工作目录下，先返回文件列表的大小，在返回查询的结果'''
        print("\033[34;1mview current working directory\033[0m")
        subpro_obj = subprocess.Popen('dir', shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        stdout = subpro_obj.stdout.read()
        stderr = subpro_obj.stderr.read()
        conn.send(struct.pack('i', len(stdout + stderr)))
        conn.send(stdout)
        conn.send(stderr)
        print('\033[31;1mCongratulations view directory success\033[0m')

    def mkdir(self, conn):
        '''增加目录
        在当前目录下,增加目录
        1.查看目录名是否已经存在
        2.增加目录成功,返回 1
        2.增加目录失败,返回 0'''
        print("\033[34;1madd working directory\033[0m")
        if len(self.cmds) > 1:
            mkdir_path = os.path.join(os.getcwd(), self.cmds[1])
            if not os.path.exists(mkdir_path):
                os.mkdir(mkdir_path)
                print('\033[31;1mCongratulations add directory success\033[0m')
                conn.send(struct.pack('i', 1))
            else:
                print("\033[31;1muser directory already does exist\033[0m")
                conn.send(struct.pack('i', 0))
        else:
            print("\033[31;1muser does not enter file name\033[0m")

    def cd(self, conn):
        '''切换目录
        1.查看是否是目录名
        2.拿到当前目录,拿到目标目录,
        3.判断homedir是否在目标目录内,防止用户越过自己的home目录 eg: ../../....
        4.切换成功,返回 1
        5.切换失败,返回 0'''
        print("\033[34;1mSwitch working directory\033[0m")
        if len(self.cmds) > 1:
            dir_path = os.path.join(os.getcwd(), self.cmds[1])
            if os.path.isdir(dir_path):
                # os.getcwd 获取当前工作目录
                previous_path = os.getcwd()
                # os.chdir改变当前脚本目录
                os.chdir(dir_path)
                target_dir = os.getcwd()
                if self.homedir_path in target_dir:
                    print(
                        '\033[31;1mCongratulations switch directory success\033[0m')
                    conn.send(struct.pack('i', 1))
                else:
                    print('\033[31;1mSorry switch directory failed\033[0m')
                    # 切换失败后,返回到之前的目录下
                    os.chdir(previous_path)
                    conn.send(struct.pack('i', 0))
            else:
                print(
                    '\033[31;1mSorry switch directory failed,the directory is not current directory\033[0m')
                conn.send(struct.pack('i', 0))
        else:
            print("\033[31;1muser does not enter file name\033[0m")

    def remove(self, conn):
        """删除指定的文件,或者空文件夹
               1.删除成功,返回 1
               2.删除失败,返回 0
               """
        print("\033[34;1mRemove working directory\033[0m")
        if len(self.cmds) > 1:
            file_name = self.cmds[1]
            file_path = os.path.join(os.getcwd(), file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                conn.send(struct.pack('i', 1))
            elif os.path.isdir(file_path):  # 删除空目录
                if not len(os.listdir(file_path)):
                    os.removedirs(file_path)
                    print('\033[31;1mCongratulations remove success\033[0m')
                    conn.send(struct.pack('i', 1))
                else:
                    print('\033[31;1mSorry remove directory failed\033[0m')
                    conn.send(struct.pack('i', 0))
            else:
                print('\033[31;1mSorry remove directory failed\033[0m')
                conn.send(struct.pack('i', 0))
        else:
            print("\033[31;1muser does not enter file name\033[0m")
