import urllib.request, urllib
import requests
import time
from loguru import logger
import os

logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs","owhat.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")

@logger.catch
def getOwhatSales(raiseID):
    headers = {
        'host':'appo4.owhat.cn',
        'content-type':'application/x-www-form-urlencoded',
        'User-Agent':"Owhat Family/5.6.1 (iPhone; iOS 13.6.1; Scale/2.00)"
    }
    amount = 0
    page = 1
    while True:
        data = '{ "goodsid":"'+str(raiseID)+'","pagenum":"' + str(page)+'","pagesize":"100"}'
        params = {
            'cmd_s': 'shop.goods',
            'cmd_m': 'findrankingbygoodsid',
            'apiv': '1.0.0',
            'client': '{"platform":"ios","deviceid":"7CB22AEE-2D3F-44E9-8534-FDB4C790A3AF","channel":"AppStore","version":"5.6.1"}',
            'data': data,
            'v':'1.0'
        }

        url = "https://appo4.owhat.cn/api?client_id=3&requesttimestap=" + str(int(time.time()*1000))

        response = requests.post(url,params,json=True,headers=headers)


        resJsonData = response.json()
        length = 0
        if resJsonData["result"] != "fail":
            rankingList = resJsonData['data']['rankinglist']
            length = len(rankingList)
            for thisItem in rankingList:
                amount += float(thisItem['amount'])
        if length < 100:
            return round(amount, 2)
        page += 1

def getOwhatRaiseID(pid):
    prolist = []
    headers = {
        'host':'m.owhat.cn',
        'content-type':'application/x-www-form-urlencoded'
    }
    i = 1
    while True:
        data = '{"pagenum":' + str(i) + ',"pagesize":20,"userid":"' + str(pid)+'","tabtype":1,"goodssort":1,"ascordesc":2}'
        params = {
            'cmd_s': 'userindex',
            'cmd_m': 'home',
            'v': '5.5.0',
            'client': '{"platform":"mobile", "version":"5.5.0", "deviceid":"xyz", "channel":"owhat"}',
            'data': data
        }
        i += 1
        url = "https://m.owhat.cn/api?requesttimestap=" + str(int(time.time()*1000))

        response = requests.post(url,params,json=True,headers=headers)
        resJsonData = response.json()
        if resJsonData["result"] != "success":
            return -1
        res_pro = resJsonData["data"].get("useractivity")
        if res_pro:
            for p in res_pro:
                if int(p["entityid"]) > 100000:
                    prolist.append(p["entityid"])
            if len(res_pro) < 20:
                break
        else:
            break
    return prolist
if __name__ == "__main__":
    total = getOwhatSales(114004)
    # raiseList = getOwhatRaiseID("2581213")
    # total = 0
    # for r in raiseList:
    #     total += getOwhatSales(r)
    print(total)