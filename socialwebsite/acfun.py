from lxml import etree
import requests
import time

import shared.mongoDB as mongo
import bot.GraiaBot as bGraia
import shared.QQGroup as qqgroup

def initAcFun(name,uid):
    db = mongo.mongodb()
    ids = db.get_acfun_number(name).get("acfunids")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}
    page = 1

    while True:
        now = str(int(time.time()) * 1000)
        url = 'https://www.acfun.cn/u/{0}?quickViewId=ac-space-video-list&reqID=10&ajaxpipe=1&type=video&order=newest&page={2}&pageSize=20&t={1}'.format(uid,now,page)

        res = requests.get(url,headers=headers)
        html = res.text.replace('/*<!-- fetch-stream -->*/',"")
        html = eval(html).get("html")

        htmlEtree = etree.HTML(html)

        data = htmlEtree.xpath('//*[@id="ac-space-video-list"]/a')
        total = len(data)
        if total == 0:
            break
        for i in range(total,0,-1):
            aid = htmlEtree.xpath('//*[@id="ac-space-video-list"]/a[{}]'.format(i))[0].attrib['href'].split("/")[-1][2:]
            if ids and aid in ids:
                break
            db.db["config"].update_one({"name":"刘力菲"},{"$addToSet": {"acfunids":aid}})
        page += 1

if __name__ == "__main__":
    initAcFun("刘力菲","35221448")
    db = mongo.mongodb()
    bot = bGraia.GraiaBot()
    qq = qqgroup.pocket_groups
    while True:
        msg = "刘力菲在A站更新视频了\n标题：{}\n链接：{}"
        ids = db.get_acfun_number("刘力菲").get("acfunids")
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}
        uid = "35221448"
        page = 1
        
        while True:
            now = str(int(time.time()) * 1000)
            url = 'https://www.acfun.cn/u/{0}?quickViewId=ac-space-video-list&reqID=10&ajaxpipe=1&type=video&order=newest&page={2}&pageSize=20&t={1}'.format(uid,now,page)

            res = requests.get(url,headers=headers)
            html = res.text.replace('/*<!-- fetch-stream -->*/',"")
            html = eval(html).get("html")

            htmlEtree = etree.HTML(html)

            data = htmlEtree.xpath('//*[@id="ac-space-video-list"]/a')
            total = len(data)
            if total == 0:
                break
            for i in range(total,0,-1):
                aid = htmlEtree.xpath('//*[@id="ac-space-video-list"]/a[{}]'.format(i))[0].attrib['href'].split("/")[-1][2:]
                if ids and aid in ids:
                    continue
                db.db["config"].update_one({"name":"刘力菲"},{"$addToSet": {"acfunids":aid}})
                link = "https://www.acfun.com/v/ac"+aid
                title = htmlEtree.xpath('//*[@id="ac-space-video-list"]/a[{}]/figure//figcaption/p[1]'.format(i))[0].attrib['title']
                
                bot.send_temp_message(1084176330, [1075719810], msg.format(title, link))
            page += 1
        time.sleep(3600)
    