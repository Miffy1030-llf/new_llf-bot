import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
# __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)
from taoba.Crawler import GetPurchaseList, GetDetail, GetGoodDetail, GetRank
from taoba.Structure import rankingModel
from taoba.owhatCrawler import getOwhatSales
from taoba.lottery import Draw as Draw
import shared.Util as util
import shared.mongoDB as mongo
import time
import bot.GraiaBot as bGraia
import shared.QQGroup as qqgroup
import taoba.PKItem as pk
import random
from loguru import logger

logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs","monitor.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")
class TaobaMonitor(object):
    def __init__(self):
        self.db = mongo.mongodb()
        self.bot = bGraia.GraiaBot()

    def start_monitor(self):
        while True:
            raise_list = self.db.get_raise_list()
            for _raise in raise_list:
                qq = _raise.get("qq")
                plantform_type = _raise.get("plantform_type")
                for single_raiseId in _raise.get("raise"):
                    msg = self.monitor_single_raise(single_raiseId)
                    if msg and msg != "error" and msg != "":
                        if plantform_type == 0:
                            url = "https://www.taoba.club/#/pages/idols/detail?id=" + single_raiseId
                        else:
                            url = ""
                        msg += "*" * 20

                        msg += "\n支持🔗:" + url
                        money = self.db.get_raise_info(single_raiseId).get("current")
                        head_num = self.db.get_raise_info(single_raiseId).get("total")
                        msg += "\n当前总金额{}元， 总人数{}人\n".format(round(money,1),round(head_num,0))
                        
                        self.bot.send_group_message(qq, msg)
                        
                        msg_pk = pk.PK(str(single_raiseId)).format_msg()
                        if msg_pk:
                            self.bot.send_group_message(qq, msg_pk)
            time.sleep(2)
    @logger.catch
    def monitor_single_raise(self, _raise):
        msg = ""
        resultList = GetGoodDetail(_raise)
        ul = GetPurchaseList(_raise)
        detail = GetDetail(_raise)
        self.db.insert_raise(detail)
        if ul:
            for i in range(len(ul)):
                hashValue = util.get_hash([str(ul[i].user_id), str(ul[i].time)])
                exist = self.db.db["items"].find_one({"hash":hashValue})
                if not (exist is None):
                    continue
                uid = ul[i].user_id
                self.db.insert_item(ul[i])
                user_data = self.db.get_person_money_and_rank_this_pro(_raise, uid)
                user_name = ul[i].nickname
                if not user_data:
                    continue
                total = self.db.get_total_count_and_money_this_pro(_raise)
                if user_name:
                    if total != -1:
                        msg += "感谢{}, Ta刚刚在{}中贡献了{}元!Ta一共贡献了{}元,目前排名第{}位\n".format(
                            user_name, detail.title, round(ul[i].amount, 1), round(user_data[1], 1), user_data[0])
                        msg += "\n"
                        cards_msg = ""
                        if ul[i].amount >= 10.3:
                            cards = self.drawCard(ul[i].amount//10)
                            cards_msg = "恭喜获得刘言菲语{}".format(cards)
                            self.db.insert_cards(uid,user_name,cards)
                        head_num, money = total[0], total[1]
                        if cards_msg != "":
                            msg += cards_msg
                            msg += "\n"
                        msg += "-" * 10
                        msg += "\n"
                        self.db.update_raise(_raise, money, head_num)
            return msg
    def drawCard(self, num):
        result = list(self.db.db["pic"].find({}))
        num = int(num)
        count = len(result)
        res = []
        for i in range(num):
            drawNum = random.randint(0,count-1)
            res.append(result[drawNum].get("name").split('.')[0])
        return res
if __name__ == '__main__':
    TaobaMonitor().start_monitor()
    # print(mongo.mongodb().get_raise_info("14840").get("total"))