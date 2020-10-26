from bot.GraiaBot import GraiaBot
import bot.GraiaBot as bGraia
from shared import mongoDB
import shared.QQGroup as qqgroup
from loguru import logger
import os
import taoba.PKItem as pk
from taoba.Crawler import GetPurchaseList
import subprocess
bcc = bGraia.bcc
db = mongoDB.mongodb()
logger.add(os.path.join(os.path.dirname(__file__),"logs","autobot.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")
bot = GraiaBot()

@bcc.receiver("FriendMessage")
@logger.catch
async def private_message_handler(app: bGraia.GraiaMiraiApplication,message: bGraia.MessageChain,sender:bGraia.Friend):
    msg = message.asDisplay()
    if msg == "重启":
        try:
            os.system("pm2 restart pocket")
            os.system("pm2 restart taoba")
            await app.sendFriendMessage(sender,bGraia.MessageChain.create([bGraia.Plain("重启成功")]))
        except Exception as e:
            await app.sendFriendMessage(sender,bGraia.MessageChain.create([bGraia.Plain("请重试")]))
    elif msg == "关闭房间":
        try:
            os.system("pm2 stop pocket")
            await app.sendFriendMessage(sender,bGraia.MessageChain.create([bGraia.Plain("已成功")]))
        except Exception as e:
             await app.secdndFriendMessage(sender,bGraia.MessageChain.create([bGraia.Plain("请重试")]))
    elif msg == "重启房间":
        try:
            os.system("pm2 restart pocket")
            await app.sendFriendMessage(sender,bGraia.MessageChain.create([bGraia.Plain("已成功")]))
        except Exception as e:
             await app.sendFriendMessage(sender,bGraia.MessageChain.create([bGraia.Plain("请重试")]))
    if "add " in msg or "delete " in msg:
        name = msg.split(" ")[1]
        _id = msg.split(" ")[2]
        db
@bcc.receiver("GroupMessage")
@logger.catch
async def group_message_handler(app: bGraia.GraiaMiraiApplication, message: bGraia.MessageChain, group: bGraia.Group):
    msg = message.asDisplay()
    if group.id in qqgroup.pk_groups:
        if "中贡献了" in msg:
            msg = pk.PK().format_msg()
            if msg:
                await app.sendGroupMessage(group,bGraia.MessageChain.create([bGraia.Plain(msg)]).asSendable())
        
    # if msg == "jz" or msg == "集资":
    #     if group.id in qqgroup.auto_reply_groups: 
    #         def get_raiseUrl():
    #             raise_list = db.get_raise_list()
    #             return_list = []
    #             if raise_list:
    #                 for r in raise_list:
    #                     return_list.append(db.get_raise_url(r))
    #                 return return_list
    #             return [] 
    #         url_list = get_raiseUrl()
    #         try:
    #             msg = ""
    #             for url in url_list:
    #                 if url:
    #                     msg += "{}:{}\n".format(url["title"], url["url"])
    #                 logger.info(msg)
    #                 await app.sendGroupMessage(group,bGraia.MessageChain.create([bGraia.Plain(msg)]).asSendable())
    #         except Exception as e:
    #             await app.sendGroupMessage(group,bGraia.MessageChain.create([bGraia.Plain("现在没有jz，怎么能没有呢，快喊管理员")]).asSendable())
    # elif msg == "pk" or msg == "PK":
    #     if group.id in qqgroup.pk_groups:
    #         msg = pk.PK().format_msg()
    #         if msg:
    #             await app.sendGroupMessage(group,bGraia.MessageChain.create([bGraia.Plain(msg)]).asSendable())
       
    # elif "GNZ48-刘力菲正在直播" in msg:
    #     if group.id == 244898692:
    #         bot.send_temp_message(group,[826425389,1075719810],message.asSendable())
    #         bot.send_group_message(qqgroup.vip_group, message.asSendable())  

@bcc.receiver("MemberJoinEvent")
async def group_member_join(app: bGraia.GraiaMiraiApplication, member: bGraia.Member, group: bGraia.Group):
    logger.info("memberJoin group:{}, member:{}".format(group.id, member.id))
    if group.id in qqgroup.vip_group:
        msg = bGraia.MessageChain.create([bGraia.Plain("恭喜"), bGraia.At(member.id), bGraia.Plain("闯关成功加入到ifei保护协会\n本协会秉持守护每位ifei的宗旨会超甜营业的")]).asSendable()
        await app.sendGroupMessage(group, msg)
    elif group.id in qqgroup.auto_reply_groups:
        wel = '''
                    \n补档可戳→https://space.bilibili.com/10439/
                    菲菲美颜、既往特别曲目都在里面喔
                    单笔集资满103元即可自定义头衔哦~"
                    '''
        msg = bGraia.MessageChain.create([bGraia.Plain("欢迎新聚聚："), bGraia.At(member.id), bGraia.Plain(wel)]).asSendable()
        await app.sendGroupMessage(group, msg)

bot.app.launch_blocking()