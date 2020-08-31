import pymongo
import threading
from shared import Util
from loguru import logger
import os
class mongodb(object):
    
    _instance_lock = threading.Lock()
    def __init__(self):
        host = Util.getConfig("mongodb", "host")
        port = Util.getConfig("mongodb", "port")
        db = Util.getConfig("mongodb", "db")
        user = Util.getConfig("mongodb", "user")
        passwd = Util.getConfig("mongodb", "passwd")
        
        client = pymongo.MongoClient("mongodb://{}:{}".format(host, port))
        self.db = client[db]
        self.db.authenticate(user, passwd, mechanism='SCRAM-SHA-1')
        logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs","mongodb.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")
    
    
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance'):
    #         with mongodb._instance_lock:
    #             if not hasattr(cls, '_instance'):
    #                 mongodb._instance = super().__new__(cls)

    #         return mongodb._instance
    
    @logger.catch
    def get_raise_list(self):
        try:
            config_collection = self.db["config"]
            raise_list = config_collection.find_one({"isPK":0}, {"monitor": 1})["monitor"]
            logger.info("get raise list,{}".format(raise_list))
            return raise_list
        except Exception as e:
            logger.info("get raise list error")
            logger.error(e)
            return -1
    
    @logger.catch
    def get_raise_url(self, pid):
        try:
            url = self.db["monitor"].find_one({"pro_id": pid}, {"url": 1, "title":1})
            if url:
                return url
        except Exception as e:
            return False
    
    @logger.catch
    def insert_raise(self, purchase_info):
        try:
            config_collection = self.db["config"]
            config_collection.update_one({}, {"$addToSet": {"monitor": purchase_info.pro_id}})

            monitor_collection = self.db["monitor"]
            if not monitor_collection.find_one({"pro_id": purchase_info.pro_id},{}):
                mydict = {"title": purchase_info.title, "start": purchase_info.starttime, "end": purchase_info.endtime, "num":0, "current": 0, "total": 0,"url":"https://www.tao-ba.club/#/pages/idols/detail?id=" + purchase_info.pro_id,"pro_id":purchase_info.pro_id}
                monitor_collection.insert_one(mydict)
                logger.info("insert a raise id:{}, name:{}".format(purchase_info.pro_id, purchase_info.title))
                return True
            else:
                return False
        except Exception as e:
            logger.info("[ERROR]insert error")
            return False
        
    @logger.catch
    def insert_item(self, person):
        try:
            item_collection = self.db["items"]
            fake_hash = int(person.user_id) + int(person.time)
            item_collection.insert_one({"user_id": person.user_id, "pro_id": person.pro_id, "nickname":person.nickname, "amount": round(float(person.amount),2),"time":person.time,"fake_hash":fake_hash})
            logger.debug("insert purchase item, {},{}".format(person.nickname, person.amount))
            return True
        except Exception as e:
            logger.debug("[ERROR]insert purchase item, {},{}".format(person.nickname, person.amount))
            return False
    
    @logger.catch
    def get_item_this_pro(self,pid,time):
        try:
            item_collection = self.db["items"]
            item_list = list(item_collection.find({"pro_id": pid, "time":{"$gt":int(time)}}, {"user_id":1, "amount":1,"time":1}))
            item_len = len(item_list)
            logger.debug("get {} all items".format(pid))
            return item_list, item_len
        except Exception as e:
            logger.debug("[ERROR]get {} items".format(pid))
            return -1
        
    @logger.catch
    def get_pk_info(self):
        try:
            pkConfig = self.db["pkConfig"]
            pk_list = pkConfig.find_one({"isActivated":1},{"_id":0})
            logger.debug("get pk config success")
            return pk_list
        except Exception as e:
            return -1