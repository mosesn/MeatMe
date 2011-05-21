import cherrypy
import pymongo
from pymongo import Connection

connection = Connection()
db = connection['meetme']

class Index(object):
    def group(self,group_name=""):
        group_collection = db.Groups
        group = group_collection.find_one({"name":group_name})
        max_num = group["max"]
        cur_num = group["joined"]
        status = self.group_exist(group_name)
        if status == 2:
            #group full!
            dict_ll = self.get_lat_lng(group_name)
            return str(dict_ll["lat"]) + str(dict_ll["lng"])
        return "Group Page!"
    group.exposed = True

    def form(self):
        return "Form Page"
    form.exposed = True

    def add_member(self,group_name="",lat="",lng=""):
        group_collection = db.Groups
        try:
            group_collection.update({"name":group_name},{"pos":{"$push":{"lat":lat,"lng":lng}},"$inc":{"joined":1}},safe=True)
        except pymongo.errors.OperationFailure:
            pass
        except:
            pass

    def get_lat_lng(self,group_name=""):
        group_collection = db.Groups
        group = group_collection.find_one({"name":group_name})
        tups = group["pos"]
        num = group["max"]
        lngs = [x["lng"] for x in tups]
        lats = [x["lat"] for x in tups]
        avg_lng = reduce(lambda x,y:x+y,lngs)/num
        avg_lat = reduce(lambda x,y:x+y,lats)/num
        return {"lat":avg_lat,"lat":avg_lng}

    def group_exist(self,group_name=""):
        if not (group_name==""):
            return -1
        else:
            group_collection = db.Groups
            group = group_collection.find_one({"name":group_name})
            if group:
                if group["joined"] is not group["max"]:
                    #not full
                    return 2
                else:
                    #full
                    return 1
            else:
                return 0

    def new_group(self,group_name="",number="",lat="",lng=""):
        g_exist = group_exist(group_name)
        if g_exist == 1:
            #group does exist (BAD)
            pass
        elif g_exist == 0:
            #group does not exist (GOOD)
            pass 
        elif g_exist == -1:
            #empty group_name
            pass
        else:
            #what the fuck
            pass
    new_group.exposed = True

    def old_group(self,group_name="",lat="",lng=""):
        g_exist = group_exist(group_name)
        if g_exist == 1:
            #group does exist (GOOD)
            pass
        elif g_exist == 0:
            #group does not exist (BAD)
            pass 
        elif g_exist == -1:
            #empty group_name
            pass
        else:
            #what the fuck
            pass
    old_group.exposed = True

cherrypy.quickstart(Index())
