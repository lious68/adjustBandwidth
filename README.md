用途：自动伸缩EIP带宽  
  
使用方法：
一、安装ucloud官方sdk
#pip install ucloud-sdk-python3


二、打开config.py文件，配置必要的参数。   
#配置公私钥"""  
public_key  = ""  
private_key = ""  
project_id = "" # 项目ID 请在Dashbord 上获取  
base_url    = "https://api.ucloud.cn"  
  
run_mode = 'manual' #(auto|manual|alarm)  
#auto 自动获取项目中所有EIP  
#manual 指定EIP方式，指定EIP，放到eipIdArray[]里。  
#alarm 通过告警出来的EIP，自动获取  
eipIdArray = [] #人工填写需要自动伸缩的EIP，仅在manual模式下有效。  

method = 'static' #(dynamic|package|static) #对应三种带宽调整方法，动态调整、带宽包和静态方法  
#if dynamic  
percent = 0.5 #自动调整带宽的步长，百分比。  
#if package， parameters  
package_size = 10  #带宽包大小  
time_range = 1 #持续时间，1小时  
#if staticm  
stepBandwidth = 1 #每次扩容/缩容的带宽大小，单位M  
  
#全局通用参数  
maxBandwidth = 10  #EIP的最大带宽  
minBandwidth = 1   #EIP的最小带宽  
noAjustEip = ['eip1'] #三种模式下都有效。手动填写，不参与调整的EIPid  
durtime = 310 #下次调整带宽时间间隔，单位秒  
region = 'cn-south-02' #可用区，请参考region文件  
