import configparser
import os
import time
import hashlib
from typing import List
def getConfig(section, key):
    config = configparser.ConfigParser()
    config.read( os.path.join(os.path.dirname(__file__), 'config.ini'))
    return config.get(section, key)

def convert_timestamp_to_timestr(timestamp):
    """
    将13位时间戳转换为字符串
    :param timestamp:
    :return:
    """
    timeArray = time.localtime(timestamp / 1000)
    if timeArray.tm_zone == "UTC":
        timestamp += 8 * 3600 * 1000
        timeArray = time.localtime(timestamp / 1000)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return time_str


def convert_timestr_to_timestamp(time_str):
    """
    将时间字符串转换为时间戳
    :param time_str:
    :return:
    """
    timestamp = time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
    return timestamp

def get_hash(wordings:List[str])->str:
    md = hashlib.md5()
    for wording in wordings:
        md.update(wording.encode("utf-8"))
    return md.hexdigest()

if __name__ == "__main__":
    print(get_hash(["13003020032","198989"]))
    print("\n")
    print(get_hash(["13003020032","198989"]))