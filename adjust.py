from ucloud.core import exc
from ucloud.client import Client
import logging
from config import *
import sys, time, json


logger = logging.getLogger("ucloud")
# 或者提高日志打印级别，仅打印 WARNING 及以上的日志
logger.setLevel(logging.WARN)
client = Client({
    "region": region,
    "project_id": project_id,
    "public_key" :public_key,		#账户公私钥中的公钥
    "private_key" : private_key,		#账户公私钥中的私钥
})

class EipInterface(object):
    def __init__(self, eipid):
        self.eipid = eipid
    
    def getBandwidthUsage(self):  # 定义获取带宽利用率方法，返回带宽利用率，如，0.313
        try:
            resp = client.invoke("GetMetric", {
                "ResourceType": "eip",
                "ResourceId": self.eipid,
                "TimeRange" : "160",
                "MetricName": ["NetworkOutUsage"],
            })
        except exc.UCloudException as e:
            print(e)
        else:
            result = resp['DataSets']['NetworkOutUsage']
            if len(result) < 1:
                return None
            else: 
                return(result[0]['Value']) 

    def getEipBandwidth(self):  # 定义获取EIP信息方法，返回当前带宽大小。
        try:
            resp = client.unet().describe_eip({
                "EIPIds": [self.eipid],
            })
        except exc.UCloudException as e:
            print(e)
        else:
            # return(resp)
            return(resp['EIPSet'][0]['Bandwidth'])
    # return response['EIPSet'][0]['Bandwidth']

    def addBandwidth(self, addTo):  # 定义增加带宽的方法
        try:
            resp = client.unet().modify_eip_bandwidth({
                "Bandwidth": addTo,
                "EIPId" : self.eipid
            })
        except exc.UCloudException as e:
            print(e)
        else:
            return(resp)
    
    def reduceBandwidth(self, reduceTo):  # 定义减少带宽的方法
        try:
            resp = client.unet().modify_eip_bandwidth({
                "Bandwidth": reduceTo,
                "EIPId" : self.eipid
            })
        except exc.UCloudException as e:
            print(e)
        else:
            return(resp)

    
    def createBandwidthPackage(self):  # 定义创建带宽包的方法
        try:
            resp = client.unet().create_bandwidth_package({
                "Bandwidth": package_size,
                "EIPId" : self.eipid,
                "TimeRange":time_range
            })
        except exc.UCloudException as e:
            print(e)
        else:
            return(resp)


def getEipInfo():  # 获取EIP所有信息
    try:
        resp = client.unet().describe_eip({
            "EIPIds": [],
        })
    except exc.UCloudException as e:
        print(e)
    else:
        return(resp)

def getAllEipId():  # 从所有信息里提取EIPid，并存入数组eipIdArray里。
    eipInfor = getEipInfo()
    number = eipInfor['TotalCount']
    for i in range(number):
        eipIdArray.append(eipInfor['EIPSet'][i]['EIPId'])
    return eipIdArray


def adjustBandwidth(eipid):  # 调整带宽主逻辑
    AutoEIP = EipInterface(eipid)  # 类封装给AutoEIP，并传入参数。
    try:
        utilization = AutoEIP.getBandwidthUsage()  # 带宽使用率，通过类的方法
        if utilization != None:
            curBandwidth = AutoEIP.getEipBandwidth()  # 当前带宽，通过类的方法
            print("This EIP %s utilization is %f,and the bandwidth is %dM" % (eipid, utilization, curBandwidth))

            if adjust_method == 'static':
                # 当带宽利用率超过80%，并且当前带宽还未到最高限制带宽，每次增加设置的步长带宽。
                if utilization >= 80 and curBandwidth <= maxBandwidth:
                    newBandwidth = curBandwidth + stepBandwidth
                    AutoEIP.addBandwidth(newBandwidth)
                # 当前带宽利用率低于10%，并且当前带宽还未到最低地位带宽，每次减少设置的步长带宽。
                elif utilization <= 10 and curBandwidth > minBandwidth:
                    newBandwidth = curBandwidth - stepBandwidth
                    AutoEIP.reduceBandwidth(newBandwidth)
                else:
                    print("Do nothing,-----------> The reason is maybe bandwidth  between  maximum and minimum, or It reaches its maximum or minmum.")
            elif adjust_method == 'dynamic':
                if percent >= 0.1 and percent <= 1:
                    if utilization >= 70 and curBandwidth <= maxBandwidth:
                        newBandwidth = int(curBandwidth + curBandwidth * percent)
                        AutoEIP.addBandwidth(newBandwidth)
                    # 当前带宽利用率低于10%，并且当前带宽还未到最低地位带宽，每次减少设置的步长带宽。
                    elif utilization <= 10 and curBandwidth > minBandwidth:
                        newBandwidth = int(curBandwidth - curBandwidth * percent)
                        AutoEIP.reduceBandwidth(newBandwidth)
                    else:
                        print("Do nothing,This the max bandwidth or the min bandwidth ,please adjust")
                else:
                    print("please input percent value between 0.1 and 1")
            elif adjust_method == 'package':
                if utilization >= 0.7 and curBandwidth <= maxBandwidth:
                    AutoEIP.createBandwidthPackage()
                    print("has createBandwidthPackage")
                else:
                    print("Do nothing")
            else:
                print("please choice adjust_method")

        else:
            print("has no utilization data, do nothing,cricle go on!")

    except Exception as e:
        print(e)

def main():
    client = Client({
    "region": region,
    "project_id": project_id,
    "public_key" :public_key,		#账户公私钥中的公钥
    "private_key" : private_key,		#账户公私钥中的私钥
    })
    while True:
        if run_mode == 'manual':
            eipIdList = eipIdArray
        elif run_mode == 'auto':
            eipIdList = getAllEipId()  # 获取所有EIPID
        else:
            print('You should choice one run_mode')
        adjustEip = list(set(eipIdList).difference(set(noAdjustEip)))  # 剔除不参与的EIP。
        for i in adjustEip:
            adjustBandwidth(i)
        time.sleep(durtime)


if __name__ == '__main__':
     main()
    #print(EipInterface.getEipBandwidth('eip-xdvctmxb'))
