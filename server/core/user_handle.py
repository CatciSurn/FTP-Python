# _*_coding:utf-8_*_
import configparser
import hashlib
import os

from config import settings


class UserHandle():
    '''
    创建用户名称，密码
    如果用户存在，则返回，如果用户不存在，则注册成功
    '''

    def __init__(self, username):
        self.username = username
        self.config = configparser.ConfigParser()
        self.config.read(settings.ACCOUNTS_FILE)

    def password(self):
        '''生成用户的密码，然后加密'''
        password_inp = input(
            "\033[32;1mplease input your password>>>\033[0m").strip()
        md5_obj = hashlib.md5()
        md5_obj.update(password_inp.encode('utf-8'))
        md5_password = md5_obj.hexdigest()
        return md5_password

    def disk_quota(self):
        '''生成每个用户的磁盘配额'''
        quota = input('\033[32;1mplease input Disk quotas>>>:\033[0m').strip()
        if quota.isdigit():
            return quota
        else:
            exit('\033[31;1mdisk quotas must be integer\033[0m')

    def add_user(self):
        '''创建用户，存到accounts.ini'''
        if not self.config.has_section(self.username):
            print('\033[31;1mcreating username is :%s \033[0m' % self.username)
            self.config.add_section(self.username)
            self.config.set(self.username, 'password', self.password())
            self.config.set(self.username, 'homedir', 'home/' + self.username)
            self.config.set(self.username, 'quota', self.disk_quota())
            self.write_config()
            self.create_userhome()
            print('\033[1;32msuccessfully create userdata\033[0m')
        else:
            print('\033[1;31musername already existing\033[0m')

    def create_userhome(self):
        '''创建用户的home文件夹'''
        os.mkdir(os.path.join(settings.BASE_DIR, 'home', self.username))

    def write_config(self):
        '''写入文档'''
        with open(settings.ACCOUNTS_FILE, 'w') as f:
            self.config.write(f)

    def judge_user(self):
        '''判断用户是否存在'''
        if self.config.has_section(self.username):
            return self.config.items(self.username)
