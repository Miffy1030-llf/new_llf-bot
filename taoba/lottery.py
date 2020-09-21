import random as random
from shared.mongoDB import mongodb as mdb
import os
from loguru import logger
logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs","lottery.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")

class Gift(object):
    def __init__(self,name,ratio, target):
        self.name = name
        self.ratio = ratio
        self.target = target
    
    @logger.catch
    def draw(self):
        totalTime = int(1/self.ratio)
        drawNum = random.randint(1, totalTime)
        return self.target == drawNum

class Draw(object):
    @logger.catch
    def __init__(self):
        self.giftList = mdb().get_lottery_info()

    @logger.catch
    def draw(self, times):
        drawList = []
        result = set()
        
        for gift in self.giftList:
            drawList.append(Gift(gift.get("name"), gift.get("ratio"), gift.get("target")))
        for _ in range(times):
            for gift in drawList:
                if gift.draw():
                    result.add(gift)
        return result
    
if __name__ == "__main__":
    Draw().draw(2)