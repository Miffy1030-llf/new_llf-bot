// import SDK from './NIM_Web_SDK_v7.7.0.js'
let SDK = require('./NIM_Web_SDK_nodejs_v7.1.0.js')
const logger = require('./log.js')
const axios = require("axios");
const loadIni = require('read-ini-file')
const path = require('path')
const MongoClient = require('mongodb').MongoClient;

const fix = path.join(__dirname, 'config.ini')
const ret = loadIni.sync(fix)

const roomid = ret["pocket"]["roomid"];

const liveqq = ret["pocket"]["liveqq"].split(" ")
const messageqq = ret["pocket"]["messageqq"].split(" ")

var chatroom;
var session = ""

const host = ret["mirai"]["host"]
const port = ret["mirai"]["port"]
const url = "http://" + host + ":" + port;

const mongodbPort = ret["mongodb"]["port"]
const user = ret["mongodb"]["user"]
const passwd = ret["mongodb"]["passwd"]
const db = ret["mongodb"]["db"
]
const mongodbUrl = "mongodb://" + user + ":" + passwd + "@" + host + ":" + mongodbPort + "/" + db


  
function initNIM() {
    nim = SDK.NIM.getInstance({
        debug: true,
        appKey: ret["pocket"]["appKey"],
        account: ret["pocket"]["account"],
        token: ret["pocket"]["token"],
        onconnect: onConnect,
        onwillreconnect: onWillReconnect,
        ondisconnect: onDisconnect,
        onerror: onError,
        db: false
    });
}

/*
//
//连接成功  获取聊天室服务器地址
//
*/

function onConnect() {
    logger.info('连接成功');

    //获取聊天室服务器地址
    nim.getChatroomAddress({
        chatroomId: roomid,
        done: getChatroomAddressDone
    });
}

function getChatroomAddressDone(error, obj) {
    logger.info('获取聊天室地址' + (!error ? '成功' : '失败'), error, obj);
    address = obj.address[0];
    createChatroom(); //
}

function onWillReconnect(obj) {
    // 此时说明 SDK 已经断开连接, 请开发者在界面上提示用户连接已断开, 而且正在重新建立连接
    logger.info('即将重连');
    logger.info(obj.retryCount);
    logger.info(obj.duration);
}

function onDisconnect(error) {
    // 此时说明 SDK 处于断开状态, 开发者此时应该根据错误码提示相应的错误信息, 并且跳转到登录页面
    logger.info('丢失连接');
    if (error) {
        switch (error.code) {
            // 账号或者密码错误, 请跳转到登录页面并提示错误
            case 302:
                logger.error.info("302");
                break;
                // 重复登录, 已经在其它端登录了, 请跳转到登录页面并提示错误
            case 417:
                logger.error.info("417");
                break;
                // 被踢, 请提示错误后跳转到登录页面
            case 'kicked':
                logger.error.info("kicked");
                break;
            default:
                logger.error.info(error.code);
                break;
        }
    }
}

function onError(error) {
    logger.error(error);
}
/*
//
//连接成功  获取聊天室服务器地址
//
*/
function createChatroom() {
    chatroom = new SDK.Chatroom({
        appKey: ret["pocket"]["appKey"],
        account: ret["pocket"]["account"],
        token: ret["pocket"]["token"],
        chatroomId: roomid,
        chatroomAddresses: [
            address,
            address
        ],
        onconnect: onChatroomConnect,
        onerror: onChatroomError,
        onwillreconnect: onChatroomWillReconnect,
        ondisconnect: onChatroomDisconnect,
        // 消息
        onmsgs: onChatroomMsgs
    });
    // getMemberHistory();
    // 			addListeners();//
    // 			getFansHistory();
    // init();//初始化

}

function onChatroomConnect(chatroomInfo) {
    logger.info('进入聊天室', chatroomInfo);
    // getHistoryMsgs()
}

function onChatroomWillReconnect(obj) {
    // 此时说明 SDK 已经断开连接, 请开发者在界面上提示用户连接已断开, 而且正在重新建立连接
    logger.info('即将重连', obj);
}

function onChatroomDisconnect(error) {
    // 此时说明 SDK 处于断开状态, 开发者此时应该根据错误码提示相应的错误信息, 并且跳转到登录页面
    logger.info('丢失连接');
    if (error) {
        switch (error.code) {
            // 账号或者密码错误, 请跳转到登录页面并提示错误
            case 302:
                logger.error.info("302");
                break;
                // 重复登录, 已经在其它端登录了, 请跳转到登录页面并提示错误
            case 417:
                logger.error.info("417");
                break;
                // 被踢, 请提示错误后跳转到登录页面
            case 'kicked':
                logger.error.info("kicked");
                break;
            default:
                logger.error.info(error.code);
                break;
        }
    }
}

function onChatroomError(error, obj) {
    logger.info('发生错误', error, obj);
}

function onChatroomMsgs(msgs) {
    filterLLFMessage(msgs)
}

function getHistoryMsgs() {
    chatroom.getHistoryMsgs({
        timetag: 1614840227000,
        limit: 100,
        reverse: true,
        msgTypes: ['text'],
        done: getHistoryMsgsDone
    })
}

function getHistoryMsgsDone(error, obj) {
    // logger.info('获取聊天室历史' + (!error ? '成功' : '失败'), error, obj.msgs);
    // filterLLFMessage(obj.msgs)
    
        let data = {
            "authKey": ret["mirai"]["authKey"]
        }
        return axios.post(url + "/auth", data).then(res => {
            if (res.status == 200) {
                session = res.data.session
                data = {
                    "sessionKey": session,
                    "qq": ret["mirai"]["account"]
                }
                return axios.post(url + "/verify", data).then(res => {
                    if (res.status == 200 && res.data.msg == "success") {
                        for (var index in obj.msgs) {

                            var msg = obj.msgs[index]
                            custom = JSON.parse(msg.custom)
                            let text = custom.text
                            if (text == undefined) { 
                                continue
                            }
                            let time = new Date(msg.time).Format('yy-MM-dd hh:mm:ss')
                            
                            let axiosList = []
                            send_message = [{
                                "type": "Plain",
                                "text": text
                            }]
                            save2DB("pmsg",text,time)
                            for (var i = 0; i < messageqq.length; i++) {
                                axiosList.push(send_msg_to_group(session, messageqq[i], send_message))
                            }
                            axios.all(axiosList)
                        }
                    } else {
                        logger.info("[error]" + res.status + "\t" + res.data.msg)
                    }
                }).catch(err => {
                    logger.info(err)
                    logger.info("qq verify error")
                })
            } else {
                logger.info("[error]" + res.status + "\t" + res.data.msg)
            }
        }).catch(err => {
            logger.info(err)
            logger.info("qq auth error")
        })

  // filterLLFMessage(obj.msgs)
}

function filterLLFMessage(msgs) {
    for (var index in msgs) {
        var msg = msgs[index];
        custom = JSON.parse(msg.custom)
        var role = 0
        if (custom.user.roleId) {
            role = custom.user.roleId
        }
        var live = 0
        var miffy = ret["pocket"]["miffy"]
        if (role === 3) {
            if (msg.from === miffy) {
                logger.info('收到小飞消息', msg);
                let text = custom.text
                let time = new Date(msg.time).Format('yy-MM-dd hh:mm:ss')
                if (text) {
                    if (custom.messageType == "TEXT") {
                        message = "【刘力菲房间】\nGNZ48-刘力菲:" + text + "\n时间:" + time
                    } else if (custom.messageType == "REPLY") {
                        replyName = custom.replyName
                        replyText = custom.replyText
                        // logger.info("reply" + replyName + ":" + replyText + "\n" + text)
                        message = "【刘力菲房间】\n【翻牌】" + "[" + time + "]-GNZ48-刘力菲: " + text + "\n【被翻牌】" + replyName + ": " + replyText
                    } 
                    send_message = [{
                        "type": "Plain",
                        "text": message
                    }]
                    save2DB("pmsg",message,time)
                }
                else if (msg.text == "偶像翻牌") { 
                    question = custom.question
                    answer = custom.answer
                    message = "【刘力菲房间】\n【回答】" + "[" + time + "]-GNZ48-刘力菲: " + answer + "\n【问题】" + question
                        message = "【刘力菲房间】\n【回答】" + "[" + time + "]-GNZ48-刘力菲: " + answer + "\n【问题】" + question 
                    message = "【刘力菲房间】\n【回答】" + "[" + time + "]-GNZ48-刘力菲: " + answer + "\n【问题】" + question
                        message = "【刘力菲房间】\n【回答】" + "[" + time + "]-GNZ48-刘力菲: " + answer + "\n【问题】" + question 
                    message = "【刘力菲房间】\n【回答】" + "[" + time + "]-GNZ48-刘力菲: " + answer + "\n【问题】" + question
                        message = "【刘力菲房间】\n【回答】" + "[" + time + "]-GNZ48-刘力菲: " + answer + "\n【问题】" + question 
                    message = "【刘力菲房间】\n【回答】" + "[" + time + "]-GNZ48-刘力菲: " + answer + "\n【问题】" + question
                    send_message = [{
                        "type": "Plain",
                        "text": message
                    }]
                    save2DB("pqa",message,time)
                }
                let live_cover = custom.liveCover
                if (live_cover) {
                    logger.info("[INFO]get live")
                    live_title = custom.liveTitle
                    live_id = custom.liveId
                    live = 1
                    message = "刘力菲开直播了\n直播标题: " + live_title + "\n开始时间: " + time + "\n网页地址：https://h5.48.cn/2019appshare/memberLiveShare/index.html?id=" + live_id + "\n封面:\n"
                    send_message = [{
                        "type": "AtAll"
                    }, {
                        "type": "Plain",
                        "text": message
                    }, {
                        "type": "Image",
                        "url": "https://source.48.cn/" + live_cover
                    }]

                }

                if (msg.type === "image") {
                    logger.info("[INFO]get image")
                    message = "【刘力菲房间】\n【图片】[" + time + "]-GNZ48-刘力菲: "
                    send_message = [{
                        "type": "Plain",
                        "text": message
                    }, {
                        "type": "Image",
                        "url": msg.file.url
                        }]
                    save2DB("pimg",msg.file.url,time)
                } else if (msg.type === "audio") {
                    logger.info("[INFO]get audio")
                    message = "【刘力菲房间】\n【语音】[" + time + "]-GNZ48-刘力菲: "
                    send_message = [{
                        "type": "Plain",
                        "text": message
                    }, {
                        "type": "Voice",
                        "url": msg.file.url
                        }]
                    save2DB("pvoi",msg.file.url,time)
                } else if (msg.type === "video") {
                    logger.info("[INFO]get video")
                    message = "【刘力菲房间】\n【视频】[" + time + "]-GNZ48-刘力菲: " + msg.file.url
                    send_message = [{
                        "type": "Plain",
                        "text": message
                    }]
                    save2DB("pvid",msg.file.url,time)
                }
            } else {
                let text = custom.text
                let time = new Date(msg.time).Format('yy-MM-dd hh:mm:ss')
                if (text) {
                    if (custom.messageType == "TEXT") {
                        let nickname = custom.user.nickName
                        message = "【刘力菲房间】\n" + nickname + ":" + text + "\n时间:" + time
                    }
                    send_message = [{
                        "type": "Plain",
                        "text": message
                    }]
                }
                save2DB("pother",message,time)
            }
            
            let data = {
                "authKey": ret["mirai"]["authKey"]
            }
            return axios.post(url + "/auth", data).then(res => {
                if (res.status == 200) {
                    session = res.data.session
                    data = {
                        "sessionKey": session,
                        "qq": ret["mirai"]["account"]
                    }
                    return axios.post(url + "/verify", data).then(res => {
                        if (res.status == 200 && res.data.msg == "success") {
                            if (live === 1) {
                                axiosList = []
                                for (var i = 0; i < liveqq.length; i++) {
                                    axiosList.push(send_msg_to_group(session, messageqq[i], send_message))
                                }
                                
                                return axios.all(axiosList)
                            } else {
                                axiosList = []
                                for (var i = 0; i < messageqq.length; i++) {
                                    axiosList.push(send_msg_to_group(session, messageqq[i], send_message))
                                }
                                
                                return axios.all(axiosList)

                            }
                        } else {
                            logger.info("[error]" + res.status + "\t" + res.data.msg)
                        }
                    }).catch(err => {
                        logger.info(err)
                        logger.info("qq verify error")
                    })
                } else {
                    logger.info("[error]" + res.status + "\t" + res.data.msg)
                }
            }).catch(err => {
                logger.info(err)
                logger.info("qq auth error")
            })
        }

    }
}

Date.prototype.Format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1, // 月份
        "d+": this.getDate(), // 日
        "h+": this.getHours(), // 小时
        "m+": this.getMinutes(), // 分
        "s+": this.getSeconds(), // 秒
        "q+": Math.floor((this.getMonth() + 3) / 3), // 季度
        "S": this.getMilliseconds() // 毫秒
    };
    if (/(y+)/.test(fmt))
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + ""));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}

function send_msg_to_group(session, qq, send_message) {
    if (send_message == undefined){ 
        return axios.default
    }
    data1 = {
        "sessionKey": session,
        "target": qq,
        "messageChain": send_message
    }
    
    return axios.post(url + "/sendGroupMessage", data1).then(res => {
        if (res.status == 200) {
            logger.info(res.data)
        } else {
            logger.info("[error]" + res.status + "\t" + res.data.msg)
        }
    }).catch(err => {
        logger.info(err)
        logger.info("qq send error" + qq)
    })
}

function save2DB(type, message,time) { 
    MongoClient.connect(mongodbUrl, function(err, db) {
        if (err) { logger.info(err);db.close();return };
        
        var obj = { "type": type, "msg": message, "time": time }
        db.db("Miffy").collection("messages").insertOne(obj, function (err, res) { 
            if (err) { logger.info(err);db.close();return };
            console.log("文档插入成功");
            db.close();
        })
    });
}

initNIM()