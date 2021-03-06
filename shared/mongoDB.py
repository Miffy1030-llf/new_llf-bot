import pymongo
import threading
from shared import Util
from loguru import logger
import os
import shared.Util as util

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
            raise_list = list(config_collection.find({"monitor":1}, {"_id": 0}))
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
    def insert_new_raise(self,name,pid):
        try:
            config_collection = self.db["config"]
            config_collection.update_one({"name":name}, {"$addToSet": {"raise": pid}})
            return True
        except Exception as e:
            logger.info("[ERROR]insert new raise")
            return False
        
    def remove_new_raise(self,name,pid):
        try:
            config_collection = self.db["config"]
            config_collection.update_one({"name":name}, {"$pull": {"raise": pid}})
            return True
        except Exception as e:
            logger.info("[ERROR]remove new raise")
            return False
    
    @logger.catch
    def insert_item(self, person):
        try:
            item_collection = self.db["items"]
            hashValue = util.get_hash([str(person.user_id),str(person.time)])
            item_collection.insert_one({"user_id": person.user_id, "pro_id": person.pro_id, "nickname":person.nickname, "amount": round(float(person.amount),2),"time":person.time,"hash":hashValue})
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
    def get_pk_info(self,mainPID):
        try:
            pkConfig = self.db["pkConfig"]
            pk_list = pkConfig.find_one({"isActivated":1,"mainPID":mainPID},{"_id":0})
            logger.debug("get pk config success")
            return pk_list
        except Exception as e:
            return -1
        
    @logger.catch
    def get_total_count_and_money_this_pro(self, pid):
        try:
            rank = self.get_rank_this_pro(pid)
            count = len(rank)
            money = 0
            for r in rank:
                money += r["total"]
            logger.debug("get count and money for {}".format(pid))
            return count, round(money, 1)
        except Exception as e:
            logger.debug("[ERROR]get count and money for {}".format(pid))
            logger.exception(e)
            return -1

    @logger.catch
    def get_rank_this_pro(self, pid):
        try:
            person_after_rank = self.db['items'].aggregate(
                [
                    {
                        "$match": {
                            "pro_id": pid
                        }
                    },
                    {
                        "$group": {
                            "_id": "$user_id",
                            "total": {"$sum": "$amount"},
                        }
                    },
                    {
                        "$sort": {
                            "total": -1
                        }
                    }

                ]
            )
            person_after_rank_list = []
            for r in person_after_rank:
                person_after_rank_list.append(r)
            logger.debug("get rank in raise:{}".format(pid))
            return person_after_rank_list
        except Exception as e:
            logger.debug("[ERROR]get rank in raise:{}".format(pid))
            logger.exception(e)
            return -1
        
    @logger.catch
    def get_person_money_and_rank_this_pro(self, pid, uid):
        try:
            rank = self.get_rank_this_pro(pid)
            for i in range(len(rank)):
                if rank[i].get("_id") == uid:
                    logger.debug("get {} rank and money in raise {}".format(uid, pid))
                    return i+1, rank[i].get("total")

        except Exception as e:
            logger.debug("[ERROR] get {} rank and money in raise {}".format(uid, pid))
            logger.exception(e)
            return -1
        
    @logger.catch
    def update_raise(self, pid, money, head_num):
        try:
            self.db["monitor"].update_one({"pro_id": pid}, {"$set": {"current": money, "total": head_num}})
        except Exception as e:
            logger.exception(e)
    @logger.catch
    def get_raise_info(self, pid):
        try:
            return self.db["monitor"].find_one({"pro_id": pid},{"current":1,"total":1})
        except Exception as e:
            logger.exception(e)
    
    @logger.catch
    def check_birth_status(self, pid):
        try:
            dic = {'xyyz':0,'xll':0,'llf':0,'llz':0,'other':0}
            items = list(self.db["items"].find({"pro_id":pid},{"_id":0}))
            for item in items:
                name = item["nickname"].lower()
                if 'xyyz' in name:
                    dic['xyyz'] += 1
                elif 'xll' in name:
                    dic['xll'] += 1
                elif 'llf' in name:
                    dic['llf'] += 1
                elif 'llz' in name:
                    dic['llz'] += 1
                else:
                    dic["other"] += 1
            return dic
        except Exception as e:
            return -1

    @logger.catch
    def get_weibo_ids(self,uid):
        try:
            weibo_ids = list(self.db["weibo"].find({"uid":uid},{"items":1}))
            return weibo_ids
        except Exception as e:
            logger.error(e)
            return -1
        
    @logger.catch
    def get_lottery_info(self):
        try:
            giftList = list(self.db["lottery"].find({},{"_id":0}))
            return giftList
        except Exception as e:
            logger.error(e)
            return []
        
    def get_acfun_number(self,name):
        try:
            num = self.db["config"].find_one({"name":name},{"acfunids":1})
            return num
        except Exception as e:
            return 0
if __name__ == '__main__':
    mongodb().get_lottery_info()