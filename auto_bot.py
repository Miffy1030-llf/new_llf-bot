from bot.GraiaBot import GraiaBot
import bot.GraiaBot as bGraia
from shared import mongoDB
import shared.QQGroup as qqgroup
from loguru import logger
import os
import taoba.PKItem as pk
from taoba.Crawler import GetPurchaseList
bcc = bGraia.bcc
db = mongoDB.mongodb()
logger.add(os.path.join(os.path.dirname(__file__),"logs","autobot.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")
bot = GraiaBot()

@bcc.receiver("GroupMessage")
@logger.catch
async def group_message_handler(app: bGraia.GraiaMiraiApplication, message: bGraia.MessageChain, group: bGraia.Group):
    msg = message.asDisplay()
    if msg == "jz" or msg == "集资":
        if group.id in qqgroup.auto_reply_groups: 
            def get_raiseUrl():
                raise_list = db.get_raise_list()
                return_list = []
                if raise_list:
                    for r in raise_list:
                        return_list.append(db.get_raise_url(r))
                    return return_list
                return [] 
            url_list = get_raiseUrl()
            try:
                msg = ""
                for url in url_list:
                    if url:
                        msg += "{}:{}\n".format(url["title"], url["url"])
                    logger.info(msg)
                    await app.sendGroupMessage(group,bGraia.MessageChain.create([bGraia.Plain(msg)]).asSendable())
            except Exception as e:
                await app.sendGroupMessage(group,bGraia.MessageChain.create([bGraia.Plain("现在没有jz，怎么能没有呢，快喊管理员")]).asSendable())
    elif msg == "pk" or msg == "PK":
        if group.id in qqgroup.pk_groups:
            msg = pk.PK().format_msg()
            if msg:
                await app.sendGroupMessage(group,bGraia.MessageChain.create([bGraia.Plain(msg)]).asSendable())
       
    elif "GNZ48-刘力菲正在直播" in msg:
        if group.id == 244898692:
            bot.send_group_message(qqgroup.vip_group, message.asSendable())  

@bcc.receiver("MemberJoinEvent")
async def group_member_join(app: bGraia.GraiaMiraiApplication, member: bGraia.Member, group: bGraia.Group):
    if group.id in qqgroup.vip_group:
        msg = bGraia.MessageChain.create([bGraia.Plain("恭喜"), bGraia.At(member.id), bGraia.Plain("闯关成功加入到ifei保护协会\n本协会秉持守护每位ifei的宗旨会超甜营业的")]).asSendable()
        app.sendGroupMessage(group, msg)
    elif group.id in qqgroup.auto_reply_groups:
        wel = '''
                    \n补档可戳→https://space.bilibili.com/10439/
                    菲菲美颜、既往特别曲目都在里面喔
                    单笔集资满103元即可自定义头衔哦~"
                    '''
        msg = bGraia.MessageChain.create([bGraia.Plain("欢迎新聚聚："), bGraia.At(member.id), bGraia.Plain(wel)]).asSendable()
        app.sendGroupMessage(group, msg)

def check_birth_status(pid):
    xll_list = GetPurchaseList(pid)
    allitems = {}

    for item in xll_list:
        allitems[item.user_id] = item.nickname

    llf_list = list(db.db["items"].find({"pro_id":pid}))
    for item in llf_list:
        name = item.get("nickname").lower()
        if item.get("user_id") in allitems.keys():
            if "llf" in name or "xyyz" in name or "xll" in name or "llz" in name or "刘令姿" in name:
                allitems[item.get(item.get("user_id"))] = name
        else:
            allitems[item.get(item.get("user_id"))] = name
            
    result = {"llf":[], "xll":[], "xyyz":[], "llz":[],"other":[]}   
    for uid, name in allitems.items():
        r = "{}\t{}\n".format(uid, name)
        if "llf" in name.lower():
            result["llf"].append(r)
        elif "xll" in name.lower():
            result["xll"].append(r)
        elif "xyyz" in name.lower():
            result["xyyz"].append(r)
        elif "llz" in name.lower() or "刘令姿" in name.lower():
            result["llz"].append(r)
        else:
            result["other"].append(r)
    return result
bot.app.launch_blocking()