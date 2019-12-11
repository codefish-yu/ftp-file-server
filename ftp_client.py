
from socket import *
import sys

#服务器地址
from time import sleep

ADDR = ('127.0.0.1',8888)

class FtpClient:
    '''
    实现具体功能请求
    '''
    def __init__(self,sockfd):
        self.sockfd = sockfd

    #获取文件列表
    def do_list(self):
        self.sockfd.send(b'L')   #发送请求
        #阻塞等待服务器回复
        data = self.sockfd.recv(128).decode()
        #在ok的情况下，接收filelist
        if data == 'OK':
            data = self.sockfd.recv(1024*1024).decode()
            print(data)

        #这是无文件的情况
        else:
            print(data) #目录中无文件

    # 退出
    def do_quit(self):
        self.sockfd.send(b'Q')  #协议中定了Q为退出，服务器中接到Q后，关闭为他服务的线程
        self.sockfd.close()
        sys.exit('谢谢使用')    #客户端退出

    #下载指定文件
    def do_get(self,filename):
        #发送请求
        self.sockfd.send(('G ' + filename).encode())
        #等待回复，确认文件是否存在
        data = self.sockfd.recv(128).decode()
        #接收文件
        if data == 'OK':
            #以只读方式打开filename,不存在则创建
            f = open(filename,'wb')
            while True:
                data = self.sockfd.recv(1024)
                if data == b'##':
                    break
                f.write(data)
            f.close()
        else:
            print(data)

    #上传文件
    def do_put(self,filename):#传进来的filename是绝对路径
        try:
            f = open(filename,'rb')
        except Exception:
            print('文件不存在')
            return
        #将文件名取出来
        filename = filename.split('/')[-1]

        #发送请求
        self.sockfd.send(('P ' + filename).encode())
        #等待回复
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            while True:
                data = f.read(1024)
                if not data:
                    #防止结束标志##和文件内容沾上
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            f.close()
        #
        else:
            print(data)

def main():
    sockfd = socket()
    try:    #防止这个地址拒绝我的连接，让退出更加优雅
        sockfd.connect(ADDR)
    except Exception as e:
        print(e)
        return

    #提前实例化一个对象去调用类中的不同方法
    ftp = FtpClient(sockfd) #这个类里面所有的函数都需要sockfd这个参数

    #根据不同命令发起不同请求
    while True:
        print('\n=========Command========') #命令选项提示
        print('*********  list   ********')
        print('*******  get file ********')
        print('*******   put file *******')
        print('********   quit  *********')
        print('==========================')
        cmd = input('Command:')
        if cmd.strip() == 'list':
            ftp.do_list()   #实例调用方法实现功能
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        #客户端发起下载文件请求
        elif cmd[:3] == 'get':  #通过判断请求的前三个单词是get的方法确定这时下载请求
            #获取客户端输入的要下载的文件名，并作为参数穿过去
            filename = cmd.split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3] == 'put':  #通过判断请求的前三个单词是get的方法确定这时下载请求
            #获取客户端输入的要下载的文件名，并作为参数穿过去
            filename = cmd.split(' ')[-1]
            ftp.do_put(filename)

        else:
            print('command error')







if __name__ == '__main__':
    main()