# _*_ coding: utf-8 _*_
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from config import settings
from core import ftp_client

if __name__ == '__main__':
    run = ftp_client.FTPClient(settings.ip_port)
    run.execute()
