
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

class TaobaMonitor(object):
    def __init__(self):
        self.db = mongo.mongodb()
        self.bot = bGraia.GraiaBot()

    def start_monitor(self):
        while True:
            raise_list = self.db.get_raise_list()
            for _raise in raise_list:
                qq = _raise.get("qq")
                for single_raiseId in _raise.get("raise"):
                    msg = self.monitor_single_raise(single_raiseId)
                    if msg and msg != "error" and msg != "":
                        url = "https://www.taoba.club/#/pages/idols/detail?id=" + single_raiseId
                        msg += "\n支持🔗:" + url
                        self.bot.send_group_message([qq], msg)
                        
                        msg_pk = pk.PK(str(single_raiseId)).format_msg()
                        if msg_pk:
                            self.bot.send_group_message([qq], msg_pk)
            time.sleep(2)

    def monitor_single_raise(self, _raise):
        msg = ""
        resultList = GetGoodDetail(_raise)
        ul = GetPurchaseList(_raise)
        detail = GetDetail(_raise)
        self.db.insert_raise(detail)
        if ul:
            try:
                for i in range(len(ul)):
                    exist = self.db.db["items"].find_one({"pro_id":_raise,"time": int(ul[i].time)})
                    if not (exist is None):
                        break
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
                            msg += "*" * 20
                            msg += "\n"
                            head_num, money = total[0], total[1]

                            self.db.update_raise(_raise, money, head_num)
                        # if _raise != "8937":
                        #     if _raise == "9609":
                        #         allRank = GetRank(_raise)[:10]
                        #         allRankStr = ''.join(["{}. {}\n".format(i, allRank[i]) for i in range(len(allRank))])
                        #         msg += "*" * 20
                        #         msg += "\n当前：\n"
                        #         msg += allRankStr
                                
                        #     else:
                        #         total = self.db.get_total_count_and_money_this_pro(_raise)
                        #         try:
                        #             head_num, money = total[0], total[1]
                        #         except Exception as e:
                        #             head_num, money = 0,0
                        #         finally:
                        #             if msg != "":
                        #                 msg += "\n当前集资进度{}元\n参与人数:{}\n人均{}元\n截止{}".format(money, head_num, round(money / head_num, 1), util.convert_timestamp_to_timestr(int(detail.endtime) * 1000))
                return msg
            except Exception as e:
                print(e)
                return "error"
        
if __name__ == '__main__':
    TaobaMonitor().start_monitor()
