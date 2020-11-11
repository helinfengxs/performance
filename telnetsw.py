#!/usr/bin/env python
#coding:utf-8
'导入模块'

from telnetlib import Telnet
import time

from Util import Util

'定义类'
class TelnetClient():
    '初始化属性'
    def __init__(self):
        self.tn = Telnet()
    '定义login_host函数，用于登陆设备'
    def login_host(self,userInfo,enable=None,verbose=True):
        username = userInfo["username"].strip()
        password = userInfo["password"].strip()
        ip = userInfo["ip"].strip()
        '连接设备，try-except结构'
        try:
            self.tn.open(ip,port=23,timeout=10)
        except Exception as e:
            userInfo["log"].error(e)
            userInfo["log"].warning('%s网络连接失败' %ip)
            return False
        '输入用户名'
        self.tn.read_until(b'Username:', timeout=10)
        self.tn.write(username.encode() + b'\n')
        rely = self.tn.expect([], timeout=1)[2].decode().strip()    #读显
        if verbose:
            userInfo["log"].info(rely)
        '输入用户密码'
        self.tn.read_until(b'Password:', timeout=5)
        self.tn.write(password.encode() + b'\n')
        rely = self.tn.expect([], timeout=1)[2].decode().strip()
        self.tn.read_until(b'$:', timeout=5)
        # self.tn.write("su root".encode() + b'\n')
        # self.tn.read_until(b'Password:', timeout=5)
        # self.tn.write("73c5FqBwv7Zd".encode() + b'\n')


        self.tn.read_until(b'>', timeout=5)
        self.tn.write("sh".encode() + b'\n')
        time.sleep(1)
        if userInfo["suRoot"] != "":
            self.tn.write(userInfo["suRoot"].encode() + b'\n')
        if verbose:
            userInfo["log"].info(rely)
        '进去特权模式'
        '''if enable is not None:
            self.tn.write(b'enable\n')
            self.tn.write(enable.encode() + b'\n')
            if verbose:
                rely = self.tn.expect([], timeout=1)[2].decode().strip()
                print(rely)
                time.sleep(1)
        '''
        rely = self.tn.read_very_eager().decode()
        if 'Login invalid' not in rely:
            userInfo["log"].info('%s登陆成功' % ip)
            return True
        else:
            userInfo["log"].warning('%s登陆失败，用户名或密码错误' % ip)
            return False

    '定义do_cmd函数,用于执行命令'
    def do_cmd(self,userinfo):
        # self.tn.write("su root".encode().strip() + b'\n')
        # time.sleep(1)
        # self.tn.write("73c5FqBwv7Zd".encode().strip() + b'\n')

        util = Util()

        self.executeTop(userinfo,util)



    '定义logout_host函数，关闭程序'
    def logout_host(self):
        self.tn.close()

    '定义将返回结果写入到文件'
    def run(self,userInfo):
        # lists = 'lists.txt'  # 存放IP地址文件，相对路径
        # cmds = 'cmd.txt'  # 存放执行命令文件，相对路径
        telnet_client = TelnetClient()
        # '读取文件，for语句循环登陆IP'
        # with open(lists,'rt') as list_obj:
        #     for ip in list_obj:
        '如果登录结果为True，则执行命令，然后退出'
        if telnet_client.login_host(userInfo):
                time.sleep(1)
                telnet_client.do_cmd(userInfo)
                telnet_client.logout_host()

    def executeTop(self,userInfo,util,sort=1):
        cmhiPid = ""
        gatewayPid= ""
        while (True):
            now = int(time.time())
            if (now > userInfo["runTime"]):
                userInfo["log"].info("已到设定时间, 停止top命令,开始写入数据,")
                break
            #  1表示 读取教育网插件进程，并获取教育加速进程相信内存信息
            if userInfo["type"] == 1:
                self.tn.write("top -n 1 | grep ./cmhi_acc".encode().strip() + b'\n')
                time.sleep(1)
                if cmhiPid == "":
                    cmhiPid = util.getCmhiPid()
                else:
                    time.sleep(1)
                    cmmond = "cat /proc/%s/status"%(cmhiPid)
                    self.tn.write(cmmond.encode().strip() + b'\n')
            # 游戏插件
            else:
                self.tn.write("top -n 1 | grep gateway_cmcc".encode().strip() + b'\n')
                time.sleep(1)
                if gatewayPid == "":
                    gatewayPid = util.getGateWayPid()
                else:
                    time.sleep(1)
                    cmmond = "cat /proc/%s/status"%(gatewayPid)
                    self.tn.write(cmmond.encode().strip() + b'\n')

            time.sleep(1)
            self.tn.write("free | grep Mem".encode().strip() + b'\n')
            time.sleep(1)
            self.tn.write("cat /proc/meminfo".encode().strip() + b'\n')
            time.sleep(1)
            self.tn.write("mpstat 1 2 | grep Average | grep all".encode().strip() + b'\n')
            self.tn.write(b'\n')
            time.sleep(5)
            self.tn.write("top -n 1  | grep CPU | grep idle".encode().strip() + b'\n')
            self.tn.write(b'\n')
            time.sleep(1)
            rely = self.tn.read_very_eager().decode() + "\n"
            userInfo["log"].info(rely)
            util.processingData(userInfo,rely)

        util.test(userInfo)
        #     util.splitTop(rely,pid) #正则匹配top执行后的CPU MEM数据
        #     util.writeFile(topPath,rely+"\n")
        # util.resulHandle()
        # util.writeExcel(result,None,filepath)



