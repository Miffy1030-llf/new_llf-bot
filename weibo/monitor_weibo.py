import json
import requests
from loguru import logger
import time, os

logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs","weibo.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")

class weiboMonitor(object):
    def __init__(self, uuids):
        self.uuids = uuids
        self.session = requests.session()
        self.reqHeaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://passport.weibo.cn/signin/login',
            'Connection': 'close',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        }
    
    @logger.catch  
    def monitor_singer(self,uuid):
        user_info = 'https://m.weibo.cn/api/container/getIndex?uid=%s&type=uid&value=%s' % (
            uuid, uuid)
        con_id = ''
        try:
            r = self.session.get(user_info, headers=self.reqHeaders)
            for i in r.json()['data']['tabsInfo']['tabs']:
                if i['tab_type'] == 'weibo':
                    con_id = i['containerid']
                    # TODO: 拿不到con_id
        except Exception as e:
           logger.error(e)
           
        weibo_info = 'https://m.weibo.cn/api/container/getIndex?uid=%s&type=uid&value=%s&containerid=%s' % (
            uuid, uuid, con_id)
        
        try:
            r = self.session.get(weibo_info, headers=self.reqHeaders)
            itemIds = []  # WBQueue
            for i in r.json()['data']['cards']:
                if i['card_type'] == 9:
                    task.itemIds.append(i['mblog']['id'])
                    whole_weibo_text = self.get_whole_weibo_content(i['mblog']['id'])
                    my_logger.debug('微博内容: {}'.format(
                        self.handle_weibo_text(whole_weibo_text)))
                    if 'pics' in i['mblog'].keys():
                        my_logger.debug('有图片')
                        for j in i['mblog']['pics']:
                            if 'large' in j.keys():
                                my_logger.debug('使用大图')
                                my_logger.debug(j['large']['url'])
                            else:
                                my_logger.debug(j['url'])
                    # 如果有视频
                    if 'page_info' in i['mblog'].keys():
                        page_info = i['mblog']['page_info']
                        if page_info['type'] == 'video':
                            my_logger.debug('有视频')
                            my_logger.debug('视频截图: {}'.format(page_info['page_pic']['url']))
                    # 如果是转发
                    if 'retweeted_status' in i['mblog'].keys():
                        retweeted_status = i['mblog']['retweeted_status']
                        retweeted_user = retweeted_status['user']
                        my_logger.debug(
                            '被转发人, id: {}, 微博名: {}'.format(retweeted_user['id'], retweeted_user['screen_name']))
                        my_logger.debug('转发微博内容: {}'.format(
                            self.handle_weibo_text(self.get_whole_weibo_content(retweeted_status['id']))))
            self.echoMsg('Info', 'Got weibos')
            self.echoMsg('Info', 'Has %d weibo id(s)' % len(task.itemIds))
        except Exception as e:
            self.echoMsg('Error', e)
            print(e)