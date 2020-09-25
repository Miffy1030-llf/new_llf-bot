
from taoba.Crawler import GetPurchaseList, GetDetail, GetGoodDetail, GetRank
from taoba.Structure import rankingModel
from taoba.owhatCrawler import getOwhatSales
from taoba.lottery import Draw as Draw
import shared.Util as util
import shared.mongoDB as mongo
import time
import bot.GraiaBot as bGraia
import shared.QQGroup as qqgroup


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
                        url = "https://www.tao-ba.club/#/pages/idols/detail?id=" + single_raiseId
                        msg += "\n支持🔗:" + url
                        self.bot.send_group_message([qq], msg)
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
                            if _raise == "8937":
                                gua_now = 0
                                hua_now = 0

                                total_dict = {
                                    "gua": 0, "hua": 0, "other": 0}
                                for res in resultList:
                                    if "瓜" in res[0]:
                                        total_dict["gua"] += (
                                            int(res[1]) * float(res[2]))
                                        gua_now += int(res[1])

                                    elif "花" in res[0]:
                                        total_dict["hua"] += (
                                            int(res[1]) * float(res[2]))
                                        hua_now += int(res[1])

                                record = self.db.db["config"].find_one(
                                    {"gh": 1})
                                hua = record.get("hua")
                                gua = record.get("gua")
                                if hua != hua_now:
                                    msg += "感谢{}支持了菲菲是花阵营，花妈阵营加{}积分".format(
                                        user_name, round(ul[i].amount, 1))
                                    self.db.db["config"].update(
                                        {"gh": 1}, {"$set": {"hua": hua_now}})
                                elif gua != gua_now:
                                    msg += "感谢{}支持了菲菲是瓜阵营，瓜妈阵营加{}积分".format(
                                        user_name, round(ul[i].amount, 1))
                                    self.db.db["config"].update(
                                        {"gh": 1}, {"$set": {"gua": gua_now}})
                                if total_dict.get("gua") >= total_dict.get("hua"):
                                    msg += "\n当前排名：\n瓜妈阵营{}积分，\n花妈阵营{}积分".format(
                                        round(total_dict.get("gua"), 1), round(total_dict.get("hua"), 1))
                                else:
                                    msg += "\n当前排名：\n花妈阵营{}积分，\n瓜妈阵营{}积分".format(
                                        round(total_dict.get("hua"), 1), round(total_dict.get("gua"), 1))
                            else:
                                
                                msg += "感谢{}, Ta刚刚在{}中贡献了{}元!Ta一共贡献了{}元,目前排名第{}位\n".format(
                                    user_name, detail.title, round(ul[i].amount, 1), round(user_data[1], 1), user_data[0])
                                msg += "*" * 20
                                msg += "\n"
                                head_num, money = total[0], total[1]

                                self.db.update_raise(_raise, money, head_num)
                if _raise != "8937":
                    if _raise == "9609":
                        allRank = GetRank(_raise)[:10]
                        allRankStr = ''.join(["{}. {}\n".format(i, allRank[i]) for i in range(len(allRank))])
                        msg += "*" * 20
                        msg += "\n当前：\n"
                        msg += allRankStr
                        
                    else:
                        total = self.db.get_total_count_and_money_this_pro(_raise)
                        try:
                            head_num, money = total[0], total[1]
                        except Exception as e:
                            head_num, money = 0,0
                        finally:
                            if msg != "":
                                msg += "\n当前集资进度{}元\n参与人数:{}\n人均{}元\n截止{}".format(money, head_num, round(money / head_num, 1), util.convert_timestamp_to_timestr(int(detail.endtime) * 1000))
                return msg
            except Exception as e:
                print(e)
                return "error"
        
if __name__ == '__main__':
    TaobaMonitor().start_monitor()
