
from taoba.Crawler import GetPurchaseList, GetDetail, GetGoodDetail
from taoba.Structure import rankingModel
from taoba.owhatCrawler import getOwhatSales
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

            if raise_list != -1:
                for i in range(len(raise_list)):
                    _raise = raise_list[i]
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
                                # self.db.update_or_insert_person(ul[i])
                                user_data = self.db.get_person_money_and_rank_this_pro(
                                    _raise, uid)
                                user_name = ul[i].nickname
                                if not user_data:
                                    continue
                                total = self.db.get_total_count_and_money_this_pro(
                                    _raise)
                                if user_name:
                                    # l, rank = self.db.get_item_this_pro(_raise, 0)
                                    if total != -1:
                                        msg = ""
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
                                                msg = "感谢{}支持了菲菲是花阵营，花妈阵营加{}积分".format(
                                                    user_name, round(ul[i].amount, 1))
                                                self.db.db["config"].update(
                                                    {"gh": 1}, {"$set": {"hua": hua_now}})
                                            elif gua != gua_now:
                                                msg = "感谢{}支持了菲菲是瓜阵营，瓜妈阵营加{}积分".format(
                                                    user_name, round(ul[i].amount, 1))
                                                self.db.db["config"].update(
                                                    {"gh": 1}, {"$set": {"gua": gua_now}})
                                            if total_dict.get("gua") >= total_dict.get("hua"):
                                                msg += "\n当前排名：\n瓜妈阵营{}积分，\n花妈阵营{}积分".format(
                                                    round(total_dict.get("gua"), 1), round(total_dict.get("hua"), 1))
                                            else:
                                                msg += "\n当前排名：\n花妈阵营{}积分，\n瓜妈阵营{}积分".format(
                                                    round(total_dict.get("hua"), 1), round(total_dict.get("gua"), 1))
                                            msg += "\npick🔗：https://www.taoba.club/index/#/pages/idols/detail?id=8937"
                                            self.bot.send_group_message(
                                                qqgroup.tb_groups, msg)
                                        else:
                                            url = "https://www.tao-ba.club/#/pages/idols/detail?id=" + _raise
                                            msg1 = "感谢{}, Ta刚刚在{}中贡献了{}元!Ta一共贡献了{}元,目前排名第{}位\n".format(
                                                user_name, detail.title, round(ul[i].amount, 1), round(user_data[1], 1), user_data[0])
                                            msg1 += "*" * 20
                                            msg1 += "\n"
                                            head_num, money = total[0], total[1]
                                            msg1 += "\n当前集资进度{}元\n参与人数:{}\n人均{}元\n链接{}\n截止{}".format(money,    head_num, round(
                                                money / head_num, 1), url, util.convert_timestamp_to_timestr(int(detail.endtime) * 1000))

                                            # msg += "当前集资参与人数:{}\n".format(head_num)
                                            self.db.update_raise(
                                                _raise, money, head_num)
                                            if _raise == "8876":
                                                self.bot.send_group_message(
                                                    [920604316], msg1)
                                            if _raise == "9334":
                                                self.bot.send_group_message(
                                                    [913371260], msg1)
                                            else:
                                                self.bot.send_group_message(
                                                    qqgroup.tb_groups, msg1)
                                # if total != -1:
                                #     url = "https://www.tao-ba.club/#/pages/idols/detail?id=" + _raise
                                #     msg1 = "感谢{}, Ta刚刚在{}中贡献了{}元!Ta一共贡献了{}元,目前排名第{}位\n".format(
                                #         user_name, detail.title, round(ul[i].amount, 1), round(user_data[1], 1), user_data[0])
                                #     msg2 = "*" * 20

                                #     head_num, money = total[0], total[1]

                                #     msg3 = "\n当前集资进度{}元\n参与人数:{}\n人均{}元\n链接{}\n截止{}".format(money, head_num, round(
                                #         money / head_num, 1), url, util.convert_timestamp_to_timestr(int(detail.endtime) * 1000))
                                #     self.db.update_raise(_raise, money, head_num)
                                #     self.bot.send_group_message(
                                #         qqgroup.tb_groups, msg1 + msg2 + msg3)

                            #         data_relay = {
                            #             103: 0, 51.5: 0, 10.3: 0, 1030: 0}
                            #         data_head = {
                            #             103: 0, 51.5: 0, 10.3: 0, 1030: 0}
                            #         name = {}
                            #         for item in ul:
                            #             if item.amount >= 10.3:
                            #                 data_relay[10.3] += 1
                            #             if item.amount >= 51.5:
                            #                 data_relay[51.5] += 1
                            #             if item.amount >= 103:
                            #                 data_relay[103] += 1
                            #             if item.amount >= 1030:
                            #                 data_relay[1030] += 1
                            #             if name.__contains__(item.user_id):
                            #                 name[item.user_id] += item.amount
                            #             else:
                            #                 name[item.user_id] = item.amount
                            #         msg = "今日接棒:\n"
                            #         time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            #         msg += "当前时间{}\n".format(time_now)
                            #         msg += "10.3棒数:{}\n".format(
                            #             data_relay[10.3])
                            #         msg += "52棒数:{}\n".format(data_relay[51.5])
                            #         msg += "103棒数:{}\n".format(data_relay[103])
                            #         msg += "1030棒数:{}\n".format(
                            #             data_relay[1030])
                            #         QQHandler.send_to_groups(self.qqgroup, msg)

                            #         for _, value in name.items():
                            #             if value >= 10.3:
                            #                 data_head[10.3] += 1
                            #             if value >= 51.5:
                            #                 data_head[51.5] += 1
                            #             if value >= 103:
                            #                 data_head[103] += 1
                            #             if value >= 1030:
                            #                 data_head[1030] += 1

                            #         f_msg = "人头统计:\n"

                            #         f_msg += "大于10.3人数 当前{}\n".format(
                            #             data_head[10.3])
                            #         f_msg += "大于52人数 当前{}\n".format(
                            #             data_head[51.5])
                            #         f_msg += "大于103人数 当前{}\n".format(
                            #             data_head[103])
                            #         f_msg += "大于1030人数 当前{}\n".format(
                            #             data_head[1030])
                            #         QQHandler.send_to_groups(
                            #             self.qqgroup, f_msg)
                            # need_detail = self.db.db["monitor"].find_one(
                            #     {"pro_id": _raise}, {"needDetail": 1})["needDetail"]
                            # if need_detail == 0:
                            #     break
                            #     gl = GetGoodDetail(_raise)
                            #     if len(gl) > 0:
                            #         g_msg = ''
                            #         for i in range(1, len(gl) + 1):
                            #             g_msg += "{}.{}:{}元\n ".format(
                            #                 i, gl[i-1][0], round(gl[i-1][1] * gl[i-1][2], 1))
                            #         QQHandler.send_to_groups(
                            #             self.qqgroup, g_msg)
                        except Exception as e:
                            print(e)
            # self.updatePK()
            time.sleep(2)

    def get_pk_config(self):
        return self.db.get_pk()

    def get_pk(self):
        pk_list = self.db.get_pk_list()
        pk = PKMonitor()
        return_list = []
        if pk_list:
            for p in pk_list:
                dic = {}
                pid = p["pid"]
                name = p["name"]
                ptype = p["plantform_type"]
                ratio = p["ratio"]
                dic = pk.get_pk_detail(ptype, pid, name)
                dic["new_amount"] = round(float(ratio) * dic["amount"], 2)
                dic["group_id"] = p["group_id"]
                return_list.append(dic)
            return_list = sorted(
                return_list, key=lambda x: x["new_amount"])[::-1]
            return return_list

    def get_raiseUrl(self):
        raise_list = self.db.get_raise_list()
        return_list = []
        if raise_list:
            for r in raise_list:
                return_list.append(self.db.get_raise_url(r))
            return return_list
        return []

    def get_data_of_raise(self, pid, time):
        item_list = self.db.get_item_this_pro(pid, time)
        money_list = []
        # head_list = []
        # data_relay = {103: 0, 50.5: 0, 10.3: 0,1030:0}
        data_head = {103: 0, 10.3: 0, 1030: 0}
        if item_list != -1:
            for item in item_list:
                money_list.append(round(item["amount"], 1))
            result1 = {}
            for i in set(money_list):
                result1[i] = money_list.count(i)

        rank = self.db.get_rank_this_pro(pid)
        if rank != -1:
            for item in rank:
                if item["total"] >= 1030:
                    data_head[1030] += 1
                    data_head[103] += 1
                    data_head[10.3] += 1
                elif item["total"] >= 103:
                    data_head[103] += 1
                    data_head[10.3] += 1
                elif item["total"] >= 10.3:
                    data_head[10.3] += 1
            #     head_list.append(item["total"])
            # result = {}
            # for i in set(head_list):
            #     result[i] = head_list.count(i)
            # for key, value in result.items():
            #     if key >= 1030:
            #         data_head[1030] += value
            #     elif key >= 103:
            #         data_head[103] += value
            #     elif key >= 10.3:
            #         data_head[10.3] += value

        return result1, data_head

    def get_items_after_time(self, items, time=0):
        reutrn_items = filter(lambda item: int(item.time) > time, items)
        return list(reutrn_items)

    def get_total_money_and_head(self, detail, ul):
        us = set()
        for i in ul:
            us.add(i.user_id)
        len_us = len(us)

        money = round(float(detail.current), 2)

        return money, len_us

    def updatePK(self):
        try:
            now = time.time()
            llf = round(float(GetDetail("7666").current), 2)
            fqy = round(float(GetDetail("7661").current), 2)
            xll = round(float(GetDetail("7658").current), 2)
            if now < 1596884400:
                self.db.db["monitor"].update_one(
                    {"name": "刘力菲"}, {"$set": {"p1": llf}})
                self.db.db["monitor"].update_one(
                    {"name": "费沁源"}, {"$set": {"p1": fqy}})
                self.db.db["monitor"].update_one(
                    {"name": "谢蕾蕾"}, {"$set": {"p1": xll}})
            elif now < 1596902400:
                self.db.db["monitor"].update_one(
                    {"name": "刘力菲"}, {"$set": {"p2": llf}})
                self.db.db["monitor"].update_one(
                    {"name": "费沁源"}, {"$set": {"p2": fqy}})
                self.db.db["monitor"].update_one(
                    {"name": "谢蕾蕾"}, {"$set": {"p2": xll}})
            elif now < 1596970800:
                self.db.db["monitor"].update_one(
                    {"name": "刘力菲"}, {"$set": {"p3": llf}})
                self.db.db["monitor"].update_one(
                    {"name": "费沁源"}, {"$set": {"p3": fqy}})
                self.db.db["monitor"].update_one(
                    {"name": "谢蕾蕾"}, {"$set": {"p3": xll}})
            else:
                self.db.db["monitor"].update_one(
                    {"name": "刘力菲"}, {"$set": {"p4": llf}})
                self.db.db["monitor"].update_one(
                    {"name": "费沁源"}, {"$set": {"p4": fqy}})
                self.db.db["monitor"].update_one(
                    {"name": "谢蕾蕾"}, {"$set": {"p4": xll}})
        except Exception as e:
            return


if __name__ == '__main__':
    TaobaMonitor().start_monitor()
