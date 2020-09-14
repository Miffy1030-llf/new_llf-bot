# 0. Basic Infomation
This repository is for 'GNZ48-刘力菲应援会', which is based on mirai as a qq bot engine.

Thanks for the repository below to provide codes which are easy to use:

1. [mirai-api-http](https://github.com/project-mirai/mirai-api-http)

2. [mamoe/mirai](https://github.com/mamoe/mirai)
 
3. [Application for Graia Framework](https://github.com/GraiaProject/Application)

4. [MskAdr/Tao-Ba-Grub](https://github.com/MskAdr/Tao-Ba-Grub)

# 1. How to use

basic enviroment:

ubuntu

python3.7+

mirai

mirai-api-http

mongodb

# 1.1 Start a mirai-console

1. choose a dirctory to install miraiOK
2. download miraiOK `wget http://t.imlxy.net:64724/mirai/MiraiOK/miraiOK_linux_amd64 -O miraiOK`
3. start miraiOK 
   ```shell
   chmod +x miraiOK
    ./miraiOK
   ```
4.edit ./config.txt
```
----------
login 123456789 ppaasswwdd
```   
the '----------' in the first line is needed

5. download MiraiAPIHTTP, and put the .jar in ./plugins
   [download URL](https://github.com/project-mirai/mirai-api-http/releases)
6. edit plugins/MiraiAPIHTTP/setting.yml (create if needed) 
7. restart miraiOK

# 1.2 install python dependency

pip install -r requirements.txt

# 1.3 edit config
```
cd ./shared
cp config.ini.example config.ini
```

edit your qq infomation and authkey(config in plugin setting.yml)

edit your mongdb infomation

# 2. custom

You can customize your auto-reply bot in auto_bot.py which use Graia as framework. To get more infomation about this framework, you can refer to [their github repository](https://github.com/GraiaProject/Application) and [their doc](https://graiaproject.github.io/Application/)

# 3. pocket48 room message
Because of the limitations of pocket 48, I chose Netease Yunxin(netease im)'s nodejs sdk to get the messages. To get more information about NIM, please refer to [SDK](https://dev.yunxin.163.com/docs/product/IM即时通讯/SDK开发集成/Web开发集成/NodeJS).To send message to QQ, call mirai http api directly.

# Todo list
- [x] get room messgae of pocket48 
- [ ] get weibo of Miffy
- [ ] maybe customize flag for pk

# Welcome to QQ Group 244898692 to support [GNZ48-刘力菲](https://shang.qq.com/wpa/qunwpa?idkey=ad40c7004dc4ae791b3bd279d36d082fed9e90a9001f93a603c6b965921a0ab5)

