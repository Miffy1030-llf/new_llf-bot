import random as random
from shared.mongoDB import mongodb as mdb
import os
from loguru import logger
logger.add(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "lottery.log"),
           level='DEBUG',
           format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',
           rotation="10 MB")


class Gift(object):
    def __init__(self, name, ratio, target,raiseId):
        self.name = name
        self.ratio = ratio
        self.target = target
        self.raiseId = raiseId

    @logger.catch
    def draw(self,rid,times):
        if self.ratio <= 0 or self.raiseId != rid:
            return 0
        cnt = 0
        totalTime = int(1/self.ratio)
        for _ in range(times):
            drawNum = random.randint(1, totalTime)
            if self.target == drawNum:
                cnt += 1
        return cnt
                


class Draw(object):
    @logger.catch
    def __init__(self):
        self.giftList = mdb().get_lottery_info()

    @logger.catch
    def draw(self, times, rid):
        result = []
        for g in self.giftList:
            if g.get('raiseId') == rid:
                gift = Gift(g.get("name"), g.get("ratio"), g.get("target"),g.get("raiseId"))

                cnt = gift.draw(rid,times)
                
                result.extend([gift for _ in range(cnt)])
        return result


if __name__ == "__main__":
    Draw().draw(10, "1030")
