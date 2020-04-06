# _*_ coding: utf-8 _*_
import hashlib
from core import ftp_client
from core.file_func import File_func


class Md5_func(object):
    def getfile_md5(self, file_path):
        '''对文件内容进行加密，也就是保持文件的一致性'''
        md5 = hashlib.md5(File_func().readfile(file_path))
        print("md5是：\n", md5.hexdigest())
        return md5.hexdigest()

    def verification_filemd5(self, file_path, filemd5):
        # 判断下载下来的文件MD5值和server传过来的MD5值是否一致
        if self.getfile_md5(file_path) == filemd5:
            print('\033[31;1mCongratulations download success\033[0m')
        else:
            print(
                '\033[31;1mSorry download failed,download again support breakpoint continuation\033[0m')
