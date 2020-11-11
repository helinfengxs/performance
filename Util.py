import ctypes
import inspect
import os
import re
import threading
import pandas as pd
import time
import pymysql
import globalParmas
import subprocess
from openpyxl import Workbook

from download import downloadFile

total = ""
cmhiPid = ""
gatewayPid = ""
memAvailableList = []
memUsedArryList = []
memFreeList = []
systemCpuList = []
cmhiCpuList = []
vmRssList = []
memCachedList = []
gatewayList = []
topCpuList = []
memBuffersList=[]
class Util():
    wb = Workbook()
    lock = threading.Lock()

    def __init__(self):


        self.db = self.contentMysql()
        self.dataBase = self.getCursor()
    '''
        ping Baidu数据
    '''

    def pingBaiDu(self, userInfo):
        try:
            r = subprocess.Popen("ping www.baidu.com -n " + userInfo["ping"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            globalParmas.EditGlobalParmas().setpingStaus(r)
            stdout, stderr = r.communicate()


            stderr = stdout.decode('gbk', 'replace')
            userInfo["log"].info(stderr)

        except BaseException as e:
            userInfo["log"].error(str(e))

        '''
            创建线程
        '''

    def startThread(self, num,log):
        downLoadCount = 0
        try:
            if (type(num) != int or num <= 0):
                return
            threadList = []
            for i in range(0, num):
                downLoadCount += 1
                threadList.append(threading.Thread(target=downloadFile, args=(
                ('MHXY-JD-3.0.330.exe', 'http://xyq.gdl.netease.com/MHXY-JD-3.0.330.exe', downLoadCount,log,))))
            return threadList
        except BaseException as e:
            log.error(str(e))
    '''
        利用ctypes强行杀掉线程
    '''
    def _async_raise(self, tid, exctype,log):
        try:
            tid = ctypes.c_long(tid)
            if not inspect.isclass(exctype):
                exctype = type(exctype)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
            if res == 0:
                raise ValueError("invalid thread id")
            elif res != 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
                raise SystemError("PyThreadState_SetAsyncExc failed")
        except BaseException as e:
            log.error(str(e))
    '''
        强制停止线程
    '''
    def stop_thread(self, tid):
        self._async_raise(tid, SystemExit)
    def getCmhiPid(self):
        global cmhiPid
        return cmhiPid

    def setCmhiPid(self, pid):
        global cmhiPid
        cmhiPid = pid
        return cmhiPid

    def getGateWayPid(self):
        global gatewayPid
        return gatewayPid

    def setGateWayPid(self, pid):
        global gatewayPid
        gatewayPid = pid
        return gatewayPid
    def processingData(self,userInfo, data):
        # userInfo["type"], userInfo["deviceName"]
        cmhiCpu = ""
        gatewayCpu = ""
        memAvailable = re.findall('MemAvailable:(.+.)', data)
        memFree = re.findall('MemFree:(.+.)', data)
        systemCpu = re.findall('Average:(.+.)', data)
        memTotal = re.findall('MemTotal:(.+.)', data)
        memUsed = re.findall('Mem:(.+.)', data)
        memCached = re.findall('Cached:(.+.)', data)
        topCpu = re.findall('CPU:(.+.)idle',data)
        memBuffers = re.findall('Buffers:(.+.)', data)
        # 获取memCached数据
        if len(memCached) > 0:
            memCached = memCached[0].strip().split(" ")[0]
        else:
            memCached = 0
        #获取memBuffers数据
        if len(memBuffers) > 0:
            memBuffers = memBuffers[0].strip().split(" ")[0]
        else:
            memBuffers = 0
        vmRss = re.findall('VmRSS:(.+.)', data)

        # 获取插件的进程内存
        if len(vmRss) > 0:
            vmRss = vmRss[0].strip().split(" ")[0]
        else:
            vmRss = 0
        if vmRss != 0:
            vmRssList.append(vmRss)
        # 1为教育插件，其余代表游戏插件
        if userInfo["type"] == 1:
            # 初始化一个列表，添加top - n 1 | grep ./cmhi_acc命令格式化后的数据，
            # 下标0 为进程id 下标6 进程cpu,带百分号
            cmhi_acc = re.findall('(.+.)/cmhi_acc(.+.)', data)
            if len(cmhi_acc) > 0:
                cmhi_acc = cmhi_acc[0][0].strip().split(" ")
                cmhi_accList = []
                for i in cmhi_acc:
                    if i != "":
                        cmhi_accList.append(i)
                if "%" in cmhi_accList[6]:
                    cmhiCpu = cmhi_accList[6].split("%")[0]
                else:
                    cmhiCpu = cmhi_accList[6]
                global cmhiPid
                if cmhiPid == "":
                    cmhiPid = cmhi_accList[0]

        else:
            # 游戏插件CPU，并获取其进程id
            gatewayCpu = re.findall('(.+.)/tmp/acc/gateway_cmcc', data)
            if len(gatewayCpu) > 0:
                gatewayCpu = gatewayCpu[0].strip().split(" ")
                gatewayCpuList = []
                for i in gatewayCpu:
                    if i != "":
                        gatewayCpuList.append(i)
                if "%" in gatewayCpuList[6]:
                    gatewayCpu = gatewayCpuList[6].split("%")[0]
                else:
                    gatewayCpu = gatewayCpuList[6]
                global gatewayPid
                if gatewayPid == "":
                    gatewayPid = gatewayCpuList[0]
            else:
                gatewayCpu = ""
        # 获取系统cop空闲idel
        if len(systemCpu) > 0:
            systemCpu = systemCpu[0].strip().split(" ")[-1]
            if "%" in systemCpu:
                systemCpu = systemCpu.split("%")[0]

        else:
            systemCpu = "0"

        # 获取memAvailable数据
        if len(memAvailable) > 0:
            memAvailable = memAvailable[0].strip().split(" ")[0]
        else:
            memAvailable = 0
        # 获取memUsed数据
        if len(memUsed) > 0:
            memUsed = memUsed[0].strip().split(" ")
            # 初始化一个列表，添加free命令格式化后的数据，
            # 下标0 为total 下标1 为used 下标2 为free 下标3为shared 下表4为buffers
            memUsedList = []
            for i in memUsed:
                if i != "":
                    memUsedList.append(i)
            memUsed = memUsedList[1]
            memFree = memUsedList[2]
        else:
            memUsed = ""
        if len(topCpu) > 0:
            topCpu = topCpu[0].split(" ")
            topCpulist = []
            for i in topCpu:
                if i != "":
                    topCpulist.append(i)
            topCpu = topCpulist[-1]
            if "%" in topCpu:
                topCpu = topCpulist[-1].split("%")[0]
        else:
            topCpu=""
        # 设备总内存
        global total
        if total == "":
            if len(memTotal) > 0:
                memTotal = memTotal[0].strip().split(" ")[0]
                total = memTotal


        memAvailableList.append(memAvailable)
        memUsedArryList.append(memUsed)
        memFreeList.append(memFree)
        topCpuList.append(topCpu)
        memBuffersList.append(memBuffers)
        if systemCpu != "0":
            systemCpuList.append(systemCpu)
        if memCached != "0":
            memCachedList.append(memCached)
        if cmhiCpu != "0":
            cmhiCpuList.append(cmhiCpu)
        if gatewayCpu != "0":
            gatewayList.append(gatewayCpu)
        now_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        try:
            sql = "insert into %s (memAvailab,memUsed,memFree,memBuffers,memCached,systemMpstatCpu,systemTopCpu,cmhiCpu,gateWayCpu,createTime) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (userInfo["deviceName"], memAvailable, memUsed, memFree, memBuffers,memCached, systemCpu,topCpu, cmhiCpu, gatewayCpu,now_time)
            self.dataBase.execute(sql)
            self.db.commit()
        except Exception as e:
            userInfo["log"].error(e)
            print(e)
    def test(self, userInfo):
        try:
            if userInfo["type"] == 1:
                name = "教育插件VmRss"
            else:
                name = "游戏插件VmRss"
            writer = pd.ExcelWriter(userInfo["fileName"])
            data = {'memAvailab': memAvailableList,
                    'memBuffes':memBuffersList,
                    'memUsed': memUsedArryList,
                    'memFree': memFreeList,
                    'memCached': memCachedList,
                    'mpstatemCpu': systemCpuList,
                    'topCpu':topCpuList,
                    'cmhiCpu': cmhiCpuList,
                    "gatewayCpu": gatewayList,
                    name: vmRssList}
            userInfo["log"].info(data)
            df = pd.DataFrame.from_dict(data, orient='index').transpose()
            df.to_excel(writer, sheet_name="result", index=0)
            computeResult = self.computeData(userInfo)
            dd = pd.DataFrame.from_dict(computeResult, orient='index').transpose()
            dd.to_excel(writer, sheet_name="result1", index=0)
            writer.save()
            writer.close()
            userInfo["log"].info("数据写入完毕")
            self.dataBase.close()  # 数据写完，关闭数据库连接
            self.db.close()
        except Exception as e:
            userInfo["log"].error(e)

    def computeData(self, userInfo):
        try:
            result = {}
            if userInfo["type"] == 1:
                name = "cmhi_acc内存占用"
            else:
                name = "gateway内存占用"
            global total
            if total != '':
                total = int(total)

            # 计算memuUsed/total
            memusedtotal = 0
            for i in memUsedArryList:
                if i != "":
                    memusedtotal = memusedtotal + int(i)
                list = []
                list.append(memusedtotal / len(memUsedArryList) / total)
            result["memUsed/memTotal"] = list

            # 内存计算方法 (memTotal -memAvailable)/memTotal
            memAvailabletotal = 0
            for i in memAvailableList:
                if i != "":
                    memAvailabletotal = memAvailabletotal + int(i)

            list2 = []
            list2.append((total - memAvailabletotal / len(memAvailableList)) / total)
            result["(memTotal -memAvailable)/memTotal"] = list2

            # 内存计算方法 1-(MemFree+Cached)/MemTotal

            memfreeTotal = 0
            memCachedTotal = 0
            for i in memFreeList:
                if i != "":
                    memfreeTotal = memfreeTotal + int(i)
            for i in memCachedList:
                memCachedTotal = memCachedTotal + int(i)

            list3 = []
            list3.append(1 - (memfreeTotal / len(memFreeList) + memCachedTotal / len(memCachedList)) / total)
            result["1-(MemFree+Cached)/MemTotal"] = list3

            #计算内存方法 MemTotal-MemFree-Buffers-Cached / MemTotal

            memBuffersTotal = 0
            for i in memBuffersList:
                memBuffersTotal = memBuffersTotal + int(i)
            list8 = []
            list8.append((total-memCachedTotal/len(memCachedList)-memBuffersTotal/len(memBuffersList)-memfreeTotal/len(memFreeList))/total)
            result["MemTotal-MemFree-Buffers-Cached / MemTotal"] = list8

            # 计算系统mpstat命令 cpu，idel平均值
            systemCpuTotal = 0
            for i in systemCpuList:
                if i != "":
                    systemCpuTotal = systemCpuTotal + float(i)

            list4 = []
            list4.append(100-systemCpuTotal / len(systemCpuList))
            result["mpstat命令设备cpu，idel平均值"] = list4
            #计算系统top命令 cpu，idel平均值
            systemTopCpuTotal = 0
            for i in topCpuList:
                if i != '':
                    systemTopCpuTotal = systemTopCpuTotal + float(i)
            list7 = []
            list7.append(100-systemTopCpuTotal/len(topCpuList))
            result["top命令设备cpu，idel平均值"] = list7


            if userInfo["type"] == 1:
                # 计算教育插件占用cpu平均值
                if len(cmhiCpuList) > 0:
                    cmhiCpuTotal = 0
                    for i in cmhiCpuList:
                        if i != "":
                            cmhiCpuTotal = cmhiCpuTotal + float(i)
                    list5 = []
                    list5.append(cmhiCpuTotal / len(cmhiCpuList))
                    result["cmhi_acc占用cpu均值"] = list5
            else:
                if len(gatewayList) > 0:
                    gatewayCpuTotal = 0
                    for i in gatewayList:
                        if i != "":
                            gatewayCpuTotal = gatewayCpuTotal + float(i)
                    list5 = []
                    list5.append(gatewayCpuTotal / len(gatewayList))
                    result["gateway占用cpu均值"] = list5
            if len(vmRssList) > 0:
                cmhiVRssTotal = 0
                for i in vmRssList:
                    if i != "":
                        cmhiVRssTotal = cmhiVRssTotal + int(i)
                list6 = []
                list6.append(cmhiVRssTotal / len(vmRssList) / total)
                result[name] = list6
            return result
        except Exception as e:
            print(e)
            userInfo["log"].error(e)

    '''
    连接数据库
    '''
    def contentMysql(self):
        try:
            db = pymysql.connect()
            return db
        except Exception as e:
            print(e)

    def getCursor(self):
        try:
            return self.db.cursor()
        except Exception as e:
            print(e)
    def checkMysqlTable(self, tableName):

        table_name = tableName
        if (self.table_exists(table_name) != 1):
            result = False  # 不存在
        else:
            result = True  # 存在
        return result
    def table_exists(self, table_name):  # 这个函数用来判断表是否存在
        sql = "show tables;"
        self.dataBase.execute(sql)
        tables = [self.dataBase.fetchall()]
        table_list = re.findall('(\'.*?\')', str(tables))
        table_list = [re.sub("'", '', each) for each in table_list]
        if table_name in table_list:
            return 1  # 存在返回1
        else:
            return 0
    def createTable(self, tableName):
        if not self.checkMysqlTable(tableName):
            sql = '''
                    CREATE TABLE `%s`  (
                      `id` int(11) NOT NULL AUTO_INCREMENT,
                      `memAvailab` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `memUsed` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `memFree` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `memBuffers` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `memCached` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `systemMpstatCpu` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `systemTopCpu` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `cmhiCpu` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `gateWayCpu` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      `creatTime` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
                      PRIMARY KEY (`id`) USING BTREE
                ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic
            ''' % (tableName)

            self.dataBase.execute(sql)
            sql = "SET FOREIGN_KEY_CHECKS = 1"
            self.dataBase.execute(sql)

    def mkdir(self,path):
        isData = os.path.exists(path)
        if not isData:
            os.makedirs(path)
