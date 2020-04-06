## 原作者:zhanzhengrecheng
## 修改者:wuzhong233
## 版本：示例版本 v0.1
## 程序介绍:
- 实现了基于线程开发一个FTP服务器的常用功能
- 基本功能全部用python的基础知识实现,用到了socket\hashlib\configparse\os\sys\pickle\函数\模块\类知识
- 在保证了支持多并发的功能上，不使用SocketServer模块，自己实现了多线程，而且使用了队列
 
## 概述
本次作业文件夹一共包含了以下4个文件：
- 程序结构图：整个Thread_based_FTP_homework的程序文件结构
- 程序结构文件：整个Thread_based_FTP_homework的程序文件结构
- 程序文件: Thread_based_FTP_homework
- 程序说明文件：README.md
 
## 程序要求
- 1.用户加密认证
- 2.允许同时多用户登录
- 3.每个用户有自己的家目录 ，且只能访问自己的家目录
- 4.对用户进行磁盘配额，每个用户的可用空间不同
- 5.允许用户在ftp server上随意切换目录
- 6.允许用户查看当前目录下文件
- 7.允许上传和下载文件，保证文件一致性(md5)
- 8.文件传输过程中显示进度条
- 9.附加功能：支持文件的断点续传
 
- 10.在之前开发的FTP基础上，开发支持多并发的功能 
- 11.不能使用SocketServer模块，必须自己实现多线程 
- 12.必须用到队列Queue模块，实现线程池 
- 13.允许配置最大并发数，比如允许只有10个并发用户
 
## 本项目思路
- 1 对于此次项目，在上次作业的基础上完成
- 2 本次首要任务，为了降低程序的耦合性，将把server端和client端的许多东西分出来，保证一个函数只做一件事情
- 3 发现了上次作业里面出现的小问题，进行了解决
- 4 使用队列Queue模块，实现多线程
- 5 设置配置最大的并发数，此处设置在settings里面，最大并发用户设置为3
## 更新 
 支持图片收发功能,改进了断点续传的结构模式,添加断点续传到多线程

##### 备注（程序结构）
> 目前还不会把程序树放在README.md里面，所以做出程序结构的txt版本和图片版本，放在文件外面方便查看
 
## 对几个实例文件的说明
### 几个实例文件全是为了上传和下载使用，自己随便找的素材，没有把视频，照片上传
 
## 不足及其改进的方面
### 每次程序从用户登陆到使用只能完成一次功能，不能重复使用
 
## 程序结构
 
 
│  Thread_based_FTP_homework
│  __init__.py
│  
├─client                # 客户端程序入口
│  │  __init__.py
│  ├─bin                # 可执行程序入口目录
│  │      run.py
│  │      __init__.py
│  ├─config             # 配置文件目录
│  │  │  settings.py    # 配置文件
│  │  │  __init__.py       
│  ├─core                          # 主要逻辑程序目录
│  │  │  file_func.py              # client端文件操作功能模块
│  │  │  ftp_client.py             # client端主程序模块
│  │  │  md5_func.py               # client端对文件加密操作功能模块
│  │  │  progress_bar_func_func.py # client端文件下载进度条操作功能模块
│  │  │  __init__.py       
│  ├─download           # 下载内容模块
│  │      a.txt
│  │      b.txt
│  │      c.txt  
│  └─upload             # 上传内容模块
│          a.txt
│          b.txt
└─server                 # 服务端程序入口
    ├─bin
    │      run.py        # 可执行程序入口目录
    │      __init__.py 
    ├─config             # 配置文件目录
    │  │  accounts.ini   # 账号密码配置文件
    │  │  settings.py    # 配置文件
    │  │  __init__.py        
    ├─core               # 主要逻辑程序目录
    │  │  ftp_server.py  # server端主程序模块
    │  │  main.py        # 主程序模块
    │  │  user_handle.py # 用户注册登录模块  
    │  │  file_func.py   # server端文件操作功能模块
    │  │  auth.py   	 # server端用户认证功能模块
    │  │  md5_func.py    # server端对文件加密操作功能模块
    └─home               # 家目录
        │  __init__.py
        ├─curry          # curry用户的家目录
        │  │  a.txt
        │  │  b.txt
        │  │  c.txt
        ├─durant         # durant用户的家目录
        │  └─test3
        │  └─test4
        └─james           # james用户的家目录
            │  a.txt
            │  b.txt
            │  c.txt
            │  test1
            │  test2
            └─test3