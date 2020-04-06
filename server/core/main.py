# _*_ coding: utf-8 _*_
from core.user_handle import UserHandle
from core.ftp_server import FTPServer
from config import settings


class Manager():
    '''
    主程序，包括启动server，创建用户，退出
    :return:
    '''

    def __init__(self):
        pass

    def start_ftp(self):
        '''启动server端'''
        server = FTPServer(settings.ip_port)
        server.server_link()
        server.close()

    def create_user(self):
        '''创建用户，执行创建用户的类'''
        username = input(
            "\033[32;1mplease input your username>>>\033[0m").strip()
        UserHandle(username).add_user()

    def logout(self):
        '''
        退出登陆
        :return:
        '''
        print("\033[32;1m-------Looking forward to your next login-------\033[0m")
        exit()

    def interactive(self):
        '''交互函数'''
        msg = '''\033[32;1m
                       1   启动ftp服务端
                       2   创建用户
                       3   退出
               \033[0m'''
        menu_dic = {
            "1": 'start_ftp',
            "2": 'create_user',
            "3": 'logout',
        }
        exit_flag = False
        while not exit_flag:
            print(msg)
            user_choice = input("Please input a command>>>").strip()
            if user_choice in menu_dic:
                getattr(self, menu_dic[user_choice])()
            else:
                print("\033[31;1myou choice doesn't exist\033[0m")
