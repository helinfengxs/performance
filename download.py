

import requests
import time
import os,globalParmas
def downloadFile(name, url,downCount,log):
    f=""
    try:
        headers = {'Proxy-Connection': 'keep-alive'}
        r = requests.get(url, stream=True, headers=headers)
        length = float(r.headers['content-length'])
        log.info("文件标记%s该文件大小:%sk**************开始下载文件**************"%(str(downCount),str(length)))
        # print("开始时间戳:"+str(time.time()))
        try:
            f = open(name, 'wb')
        except Exception as e:

            f = open(name, 'wb')
            print(e)
        count = 0
        count_tmp = 0
        now = int(time.time())
        time1 = int(time.time())
        for chunk in r.iter_content(chunk_size=512):
            if globalParmas.EditGlobalParmas().getRunStatus() == 2:
                f.close()
                break
            if chunk:
                f.write(chunk)
                count += len(chunk)
                if time.time() - time1 > 2:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1024 / 2
                    count_tmp = count
                    # print(count_tmp)
                    log.info('文件标记:'+str(downCount)+'*****'+name + ': ' + formatFloat(p) + '%' + ' Speed: ' + formatFloat(speed) + 'M/S'+"\n")
                    time1 = time.time()

        r1 = int(time.time()) - now
        log.info("文件标记%s**************文件下载完成**************"%(str(downCount)))
        log.info("单个线程下载用时%d秒,平均下载速度:%dMB/S"%(r1,(int(length)/1024/1024/r1)))
        f.close()
        os.system("del MHXY-JD-3.0.330.exe")
    except Exception as e:

        f.close()
        os.system("del MHXY-JD-3.0.330.exe")

    # time2 = int(time.time())
    # print("结束时间戳: "+str(time2))

def formatFloat(num):
    return '{:.2f}'.format(num)






