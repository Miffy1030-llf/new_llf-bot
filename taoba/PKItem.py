import os

from loguru import logger

import taoba.Crawler as taobaCrawler
import taoba.owhatCrawler as owhat
from shared.mongoDB import mongodb as mdb

logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs","pk.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")

class PK(object):
    @logger.catch
    def __init__(self):
        while 1:
            self.mdb = mdb()
            pk_info = self.mdb.get_pk_info()
            if pk_info == -1:
                continue
            self.__name = pk_info.get("name")
            self.__total_time = pk_info.get("total_time")
            self.__interval = pk_info.get("interval")
            self.__groups = pk_info.get("groups")
            self.__ratio = pk_info.get("ratio")
            self.__needTotal = pk_info.get("need_total")
            self.pk_list = []
            break
    
    @logger.catch
    def __format_basic_info(self):
        pk_list = []
        for group in self.__groups:
            name = group.get("name")
            plantform_type = group.get("plantform_type")
            pid = group.get("pid")
            ratio = group.get("ratio")
            _group = group.get("group")
            amount = self.__get_amount(plantform_type, pid)
            pk_list.append([name, amount, ratio, _group])
        self.pk_list = pk_list
    
    @logger.catch
    def __format_group_rank(self):
        pk_list = self.pk_list
        group_dict = {}
        if len(pk_list) == 0:
            return -1
        for pkinfo in pk_list:
            ratio = pkinfo[2] if self.__ratio == 1 else 1
            actual_amount = pkinfo[1]
            amount = ratio * actual_amount
            
            if pkinfo[3] in group_dict.keys():
                group_dict[pkinfo[3]]["group"].append(pkinfo)
                group_dict[pkinfo[3]]["amount"] += amount
                group_dict[pkinfo[3]]["actual_amount"] += actual_amount
            else:
                group_dict[pkinfo[3]] = {'group':[pkinfo], "amount":amount, "actual_amount":actual_amount}
        ranked_group = sorted(group_dict.items(), key=lambda v: v[1]["amount"])[::-1]
        ranked_group_list = []
        for group in ranked_group:
            g = group[1]
            ranked = sorted(g['group'], key=lambda v: v[1] * (v[2] if self.__ratio == 1 else 1))[::-1]
            ranked_group_list.append(ranked)
        
        return ranked_group,ranked_group_list
            
    @logger.catch 
    def __format_ranked_msg(self):

        ranked_group,ranked_group_list = self.__format_group_rank()
        msg = "{}当前排名：\n".format(self.__name)
        ourRank = 1
        for i in range(len(ranked_group)):
            msg += "【第{}组】总计{}元，组内排名\n".format(ranked_group[i][0], round(ranked_group[i][1].get("amount"),1))
            if ranked_group[i][1] == 1:
                ourRank = i + 1
            msg += "".join(["{}:{}元\n".format(p[0], round(p[1] * (p[2] if self.__ratio == 1 else 1),1)) for p in ranked_group_list[i]])
        if ourRank == 1:
            dis = round(ranked_group[0][1]["amount"] - ranked_group[1][1]["amount"],1)
            msg += " 我们目前为第1名， 领先第二名{}\n".format(dis)
        else:
            dis = round(ranked_group[ourRank - 2][1]["amount"] - ranked_group[ourRank -1][1]["amount"],1)
            msg += " 我们目前为第1名， 领先第二名{}\n".format(dis)
        return msg
 
        
    @logger.catch 
    def __format_total_msg(self):
        pk_list = self.pk_list
        msg = "总榜:\n"
        sorted_pk_list = sorted(pk_list, key=lambda x: x[1] *( x[2] if self.__ratio == 1 else 1))[::-1]
        for i in range(len(sorted_pk_list)):
            ratio = sorted_pk_list[2] if self.__ratio == 1 else 1
            amount = round(sorted_pk_list[i][1] * ratio, 1)
            if sorted_pk_list[i][0] == "刘力菲":
                msg += "*{}.{}: {}元\n".format(i + 1, sorted_pk_list[i][0], amount)
            else:
                msg += "{}.{}: {}元\n".format(i + 1, sorted_pk_list[i][0], amount)
        return msg
    
    def format_msg(self):
        
        self.mdb.db["pkConfig"].update_one({"isActivated":1},{"$set": {"total_time": self.__total_time + 1}})
        if self.__total_time % self.__interval != 0:
            return None
        try:
            self.__format_basic_info()
            msg = self.__format_ranked_msg()
            if self.__needTotal == 1:
                msg += ("\n" + "*" * 10 + "\n" + self.__format_total_msg())
        except Exception:
            msg = "PK可能不存在哦 但小飞的可爱是存在的"   
        finally:
            return msg
        
    @logger.catch  
    def __get_amount(self,plantform_type,pid):
        amount = 0
        if plantform_type == 0:
            detail = taobaCrawler.GetDetail(pid)
            amount = detail.current
            
        elif plantform_type == 1:
            amount = owhat.getOwhatSales(pid)
            
        return round(float(amount),2)
        
if __name__ == "__main__":
    print(PK().format_msg())
