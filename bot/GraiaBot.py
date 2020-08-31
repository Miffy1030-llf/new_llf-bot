import asyncio
import threading

from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.application.friend import Friend
from graia.application.message.elements.internal import Plain,At

from graia.broadcast import Broadcast


from shared import Util

import os
import functools

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)

def force_sync(fn):
    '''
    turn an async function to sync function
    '''
    import asyncio

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return asyncio.get_event_loop().run_until_complete(res)
        return res

    return wrapper

class GraiaBot(object):
    _instance_lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with GraiaBot._instance_lock:
                if not hasattr(cls, '_instance'):
                    GraiaBot._instance = super().__new__(cls)

            return GraiaBot._instance
        
    def __init__(self):
        
        host = Util.getConfig("mirai", "host")
        port = Util.getConfig("mirai", "port")
        authKey = Util.getConfig("mirai", "authKey")
        account = Util.getConfig("mirai", "account")
        url = "http://"+"{}:{}".format(host,port)
        self.app = GraiaMiraiApplication(
            broadcast=bcc,
            connect_info=Session(
                host=url,  # 填入 httpapi 服务运行的地址
                authKey=authKey,  # 填入 authKey
                account=account,  # 你的机器人的 qq 号
                websocket=False  # Graia `已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
            )
        )

    @force_sync
    async def sync_auth(self):
        await self.app.authenticate()
    @force_sync  
    async def sync_ac(self):
        await self.app.activeSession()
    @force_sync
    async def sync_send_group_message(self, qq, message):
        message = MessageChain.create([Plain(message)]).asSendable()
        await self.app.sendGroupMessage(qq, message)

    def activate(self):
        self.sync_auth()
        self.sync_ac()
    
    def send_group_message(self, qqGroups, message):
        self.activate()
        for qq in qqGroups:
            self.sync_send_group_message(qq, message)
