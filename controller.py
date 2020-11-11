import os
import threading
import time
import globalParmas
import requests

from download import downloadFile

import logs
import Util
def run(userInfo):
    log = logs.logs(userInfo["logName"])
    userInfo["log"] = log
    os.system("del MHXY-JD-3.0.330.exe")

    u = Util.Util()
    #写入数据库操作
    try:
        u.createTable(userInfo["deviceName"].lower())
    except Exception as e:
        log.error(e)
    #共下载的文件大小
    lenth = judgeSpeed(userInfo["downCount"])
    #初始化文件下载开始
    downFileStartTime = 0
    #初始线程列表
    threadList1 = []


    thread = u.startThread(userInfo["downCount"],log) # 控制时间内创建多少线程,例 5 就是创建五个下载文件线程
    if(thread!= None): #创建线程如果不为空

        for i in thread:
            threadList1.append(i)  # 循环已创建的线程列表,添加到threadList1列表,便于时间内下载文件完成,拉起线程
            i.start()  #启动下载线程
        downCount = 0
        downFileStartTime = float(time.time())
        while (True):
            status = globalParmas.EditGlobalParmas().getRunStatus()
            now = int(time.time())
            if (now > userInfo["runTime"] ):
                log.info("**************时间到达,停止线程下载文件**************")
                for i in threadList1:
                    log.info("**************文件下载:%s:线程停止**************" % (i.getName()))
                    u._async_raise(i.ident, SystemExit,log)
                os.system("del MHXY-JD-3.0.330.exe")
                break
            if status == 2:
                for i in threadList1:
                    log.info("**************文件下载:%s:线程停止**************" % (i.getName()))
                    u._async_raise(i.ident, SystemExit,log)
                os.system("del MHXY-JD-3.0.330.exe")
                break
            time.sleep(1)
            for i in threadList1:
                # logging.info("**************文件下载:%s线程进行中**************" % (i.getName()))
                # 判断线程是否活跃
                if (i.is_alive() == False):
                    threadList1.remove(i)  # 如果该线程已完成,从列表中删除
                    log.info("当前剩余线程数量：%d" % len(threadList1))
                    if(len(threadList1) == 0):
                        downFileEndTime = float(time.time())
                        userTime = downFileEndTime- downFileStartTime
                        log.info("总共下载用时%f,下载速率%fMB/S"%(userTime,lenth/1024/1024/userTime))
            # 重新拉起线程
            if(len(threadList1) <= 0):
                downFileStartTime = float(time.time())
                log.info("**************重新拉起文件下载进程*************")
                for i in range(0,userInfo["downCount"]):
                    downCount+=1
                    t1 = threading.Thread(target=downloadFile,
                                          args=(('MHXY-JD-3.0.330.exe', 'http://xyq.gdl.netease.com/MHXY-JD-3.0.330.exe',
                                                 downCount,log)))
                    t1.start()
                    threadList1.append(t1)  # 新线程添加到列表中

    else:
        log.info("**************不下载文件*************" )
def judgeSpeed(threadNum):
        headers = {'Proxy-Connection': 'keep-alive'}
        r = requests.get('http://xyq.gdl.netease.com/MHXY-JD-3.0.330.exe', stream=True, headers=headers)
        length = float(r.headers['content-length'])*threadNum
        r.close()
        return length

# if __name__ == '__main__':
#     scriptTime = 100   #脚本执行时间  单位秒,int数据类型
#     pingPackage = "20" #ping百度发送包量,string类型
#     threadNum =1#创建下载文件线程数,int类型
#     os.system("del MHXY-JD-3.0.330.exe")
#     userInfo = {
#         'username': 'root',
#         'password':'!@qw34er',
#         "deviceName":"gs3101",
#         "ip":"192.168.1.1",
#         "log":logs.logs("test1.log"),
#         "ping":pingPackage,
#         "downCount":threadNum,
#         "runTime":scriptTime,
#         "fileName":"11023456_1.xlsx",
#         "type":1,
#         "suRoot":""
#         }#telnet账号密码,设备名字
#
#     run(userInfo)


