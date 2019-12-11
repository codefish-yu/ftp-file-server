'''
ftp文件服务器服务端
'''

from socket import *
from threading import Thread
import os,sys

#定义全局变量
from time import sleep

HOST = '0.0.0.0'
PORT = 8888
ADDR=(HOST,PORT)

#文件库目录路径
FTP = '/home/xxx/FTP/'

#自定义线程类，然后将连接套接字传进来
class FtpServer(Thread):
    '''
    查看文件列表，上传，下载，退出
    '''
    def __init__(self,connfd):  #将和客户端通信的套接字传进来
        self.connfd = connfd
        super().__init__()

    def do_list(self):
        #获取文件列表
        files = os.listdir(FTP)
        #如果是空列表
        if not files:
            self.connfd.send('该目录下没有文件')
            return
        #否则返回ok
        else:
            self.connfd.send(b'OK')
            sleep(0.1)  #防止与后面的内容粘包

        #初始化一个容器，将所有文件名加进来
        filelist = ''
        for file in files:
            #只给客户端查看普通文件(不包括隐藏文件和文件夹)
            if file[0] != '.' and os.path.isfile(FTP+file):
                filelist += file + '\n'
        self.connfd.send(filelist.encode())

    #下载文件
    def do_get(self,filename):
        #以读方式打开文件,若文件不存在会报错，捕获异常
        try:
            f = open(FTP+filename,'rb')
        #文件不存在
        except Exception:
            self.connfd.send('vip可以下载'.encode())
            return
        else:
            self.connfd.send(b'OK')
            #防止OK和下面发送的文件内容粘在一起
        #发送文件
        while True:
            data = f.read(1024)
            #如果没有内容
            if not data:
                #防止##和文件内容沾到一起
                sleep(0.1)
                self.connfd.send(b'##')
                break
            #将文件内容发送到网络缓冲区
            self.connfd.send(data)
        f.close()

    #上传文件
    def do_put(self,filename):
        #该文件已存在的情况
        if os.path.exists(FTP+filename):
            self.connfd.send('文件已存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
        #接收文件
        f = open(FTP+filename,'wb')
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            f.write(data)
        f.close()

    #启动函数
    def run(self):
        #循环接收来自客户端的请求
        while True:
            #客户端请求
            data = self.connfd.recv(1024).decode()
            #判断请求类型并做出响应
            #如果接收到Q或者接收到的为空(客户端因为异常断开),结束线程
            if not data or data == 'Q':
                #自定义线程类，run()函数结束，线程就结束
                return
            #客户端请求获取文件列表
            elif data == 'L':
                self.do_list()
            elif data[0] == 'G':
                filename = data.split(' ')[-1]
                self.do_get(filename)
            #客户端上传文件请求
            elif data[0] == 'P':
                filename = data.split(' ')[-1]
                self.do_put(filename)



#搭建网络并发模型
def main():
    #创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)

    print('Listen the port 8888...')
    # 循环等待客户端连接
    while True:
        try:
            c,addr = s.accept()
            print('Connect from',addr)
        except KeyboardInterrupt as e:
            sys.exit('服务器退出')
        except Exception as e:
            print(e)
            continue


        #每当有客户端连接进来，就创建一个线程为其服务
        #FtpServer()是线程类，t为实例化，将连接套接字传进去
        t = FtpServer(c)
        t.setDaemon(True)   #设置主线程退出时子线程随之退出(主线程退出一般为服务端崩溃)
        t.start()   #start()启动，运行run()接口

if __name__ == '__main__':
    main()

