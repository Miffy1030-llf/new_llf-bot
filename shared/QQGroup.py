import shared.mongoDB as mongo

mdb = mongo.mongodb()

auto_reply_groups = mdb.db["config"].find_one({"isPK": 0})["autoQQGroup"]
pk_groups = mdb.db["config"].find_one({"isPK":0})["pkGroup"]
pocket_groups = mdb.db["config"].find_one({"isPK":0})["pocketQQGroup"]
tb_groups = mdb.db["config"].find_one({"isPK":0})["tbQQGroup"]
vip_group = mdb.db["config"].find_one({"isPK":0})["vipGroup"]
