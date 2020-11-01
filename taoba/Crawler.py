import requests
import zlib
import json
import base64
import time
from taoba.Structure import Project, Record
from loguru import logger
import os

logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs","taobac.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")
def AddSalt(ori:bytearray):
    #从网页JS当中提取到的混淆盐值，每隔一位做一次异或运算
    Salt = '%#54$^%&SDF^A*52#@7'
    i = 0
    for ch in ori:
        if i%2==0:
            ch = ch ^ ord(Salt[(i//2) % len(Salt)])
        ori[i]=ch
        i+=1
    return ori

def EncodeData(ori:str):
    #开头的数字是原始报文长度
    Length = len(ori)
    Message = str.encode(ori)
    #首先用zlib进行压缩
    Compressed = bytearray(zlib.compress(Message))
    #然后加盐混淆
    Salted = AddSalt(Compressed)
    #最后将结果转化为base64编码
    Result = base64.b64encode(Salted).decode('utf-8')
    #将长度头和base64编码的报文组合起来
    return str(Length) + '$' + Result

def DecodeData(ori:str):
    #分离报文长度头
    #TODO: 增加报文头长度的验证
    Source = ori.split('$')[1]
    #base64解码
    B64back = bytearray(base64.b64decode(Source))
    #重新进行加盐计算，恢复原始结果
    Decompressed = AddSalt(B64back)
    #zlib解压
    Result = zlib.decompress(Decompressed).decode('utf-8')
    #提取json
    return json.loads(Result)

def SendRequest(url:str,data:str):
    Headers = {
        'Content-Type': 'application/json', 
        'Origin': 'https://www.taoba.club', 
        'Cookie': 'l10n=zh-cn', 
        'Accept-Language': 'zh-cn', 
        'Host': 'www.tao-ba.club', 
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Mobile/15E148 Safari/604.1', 
        'Referer': 'https://www.taoba.club/', 
        'Accept-Encoding': 'gzip, deflate, br', 
        'Connection': 'keep-alive',
        
    }
    Data = EncodeData(data)
    Res = requests.post(url=url,data=Data,headers=Headers,verify=False)
    ResText = Res.text
    return DecodeData(ResText)

@logger.catch
def GetDetail(pro_id:str):
    #获得项目基本信息
    try:
    
        Data='{{"id":"{0}","requestTime":{1},"pf":"h5"}}'.format(pro_id,str(time.time()*1000))
        Response=SendRequest('https://www.taoba.club/idols/detail',Data)
        return Project(str(Response['datas']['id']),
            Response['datas']['title'],
            str(Response['datas']['start']),
            str(Response['datas']['expire']),
            str(Response['datas']['donation']),
            str(Response['datas']['sellstats'])
        )
    except Exception as e:
        print(e)
        
@logger.catch
def GetPurchaseList(pro_id:str):
    #获得所有人购买的数据，以list形式返回
    try:
        Data='{{"ismore":false,"limit":15,"id":"{0}","offset":0,"requestTime":{1},"pf":"h5"}}'.format(pro_id,int(time.time()*1000))
        Response=SendRequest('https://www.tao-ba.club/idols/join',Data)
        Founderlist = []
        Cleared = False
        pages = 0
        while not Cleared:
            for thisRecord in Response['list']:
                money = 0 if '*' in thisRecord['money'] else float(thisRecord['money'])
                Founderlist.append(Record(pro_id,
                    str(thisRecord['userid']),
                    thisRecord['nick'],
                    thisRecord['stime'],
                    money
                    
                ))
            if len(Response['list']) == 15:
                pages += 1
                Data='{{"ismore":true,"limit":15,"id":"{0}","offset":{2},"requestTime":{1},"pf":"h5"}}'.format(pro_id,int(time.time()*1000),pages*15)
                Response=SendRequest('https://www.tao-ba.club/idols/join',Data)
            else:
                Cleared = True
        return Founderlist
    except Exception as e:
        print(e)

@logger.catch
def GetGoodDetail(pro_id:str):
    Data='{{"id":"{0}","requestTime":{1},"pf":"h5"}}'.format(pro_id,str(time.time()*1000))
    Response=SendRequest('https://www.tao-ba.club/idols/detail',Data)
    goods_list = Response['datas']["goods"]
    return_list = []
    for good in goods_list:
        return_list.append((good["name"], good["sells"], good["price"]))
        # print("名称{},件数{},单价{}，总额{}".format(good["name"], good["sells"], good["price"],int(good["sells"]) * int(good["price"])))
    return_list = sorted(return_list, key=lambda x: x[1]*x[2])[::-1]
    return return_list

@logger.catch
def GetRank(pro_id:str):
    Data='{{"id":"{0}","requestTime":{1},"pf":"h5","iscoopen":0,"_version_":1}}'.format(pro_id,str(time.time()*1000))
    Response=SendRequest('https://www.tao-ba.club/idols/join/rank',Data)
    rank = [item['nick'] for item in Response["list"]]
    return rank

if __name__ == "__main__":
    # print(GetPurchaseList("8937"))
    print(GetGoodDetail("9805"))
    # # GetGoodDetail("4830")
    # GetGoodDetail("8937")
