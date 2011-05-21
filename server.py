import cherrypy
import pymongo
from pymongo import Connection
from Cheetah.Template import Template

connection = Connection()
db = connection['meetme']

class Index(object):
    def group(self,group_name=""):
        group_collection = db.Groups
        group = group_collection.find_one({"name":group_name})
        max_num = group["max"]
        cur_num = group["joined"]
        status = self.group_exist(group_name)
        namespace = {"cur_num":cur_num,"max_num":max_num}
        grouppage_t = open('grouppage.tmpl', 'r')
        self.grouppage_template = grouppage_t.read()

        if status == 2:
            namespace["full"] = 1
            #group full!
            dict_ll = self.get_lat_lng(group_name)
            namespace["map"] = dict_ll
            return str(Template(self.grouppage_template, name_space))

        else:
            namespace["full"] = 0
            namespace["map"] = None
            return str(Template(self.grouppage_template, name_space))

    group.exposed = True

    def index(self):
        homepage_t = open('homepage.tmpl', 'r')
        self.homepage_template = homepage_t.read()
        return str(Template(self.homepage_template, name_space))
    form.exposed = True

    def add_member(self,group_name="",lat="",lng=""):
        group_collection = db.Groups
        try:
            group_collection.update({"name":group_name},{"pos":{"$push":{"lat":lat,"lng":lng}},"$inc":{"joined":1}},safe=True)
        except pymongo.errors.OperationFailure:
            return False
        except:
            return False
        return True

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
