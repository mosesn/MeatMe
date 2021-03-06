import cherrypy
import pymongo
import urllib2
from simplegeo import Client
from pymongo import Connection
from Cheetah.Template import Template


connection = Connection()
db = connection['meetme']
client = Client('p2R3QHMxH3xZV6SAgeTdb6sqrxG6Qk8f','XbF4sZxLyhNDMzjykHmVysbzYtnbEtCn')


class Index(object):
    def group(self,name="",error=""):

        group_collection = db.Groups
        group = group_collection.find_one({"name":name})

        grouppage_t = open('grouppage.tmpl', 'r')
        self.grouppage_template = grouppage_t.read()

        g_exist = self.group_exist(name)
        if g_exist > 0:
            max_num = group["max"]
            cur_num = group["joined"]
            namespace = {"cur_num":cur_num,"max_num":max_num}
            namespace["error"] = error
            namespace["name"] = name

            if g_exist == 1:

            #group does exist (GOOD)

                namespace["full"] = 0
                namespace["map"] = None
#                return "Group exists"
                return str(Template(self.grouppage_template, namespace))
            elif g_exist == 2:
                namespace["full"] = 1
            #group full!
                dicti = None
                if not group["finalized"]:
                    
                    dicti = self.set_final(group)
                else:
                    dicti = group
                namespace["map"] = dicti["ll"]

#               return req
                return str(Template(self.grouppage_template, namespace))
        elif g_exist == 0:
            #error page
            return "No group \"" + name + "\" exists"
            #group does not exist (BAD)
        elif g_exist == -1:
            #error page
            return "I need a group name"
            #empty name
        else:

            return "Error!"
            #what the fuck
            #error page

    group.exposed = True

    def set_final(self,group = None):
        dict_ll = self.get_lat_lng(group)
        lat = dict_ll["lat"]
        lng = dict_ll["lng"]
        name = group["name"]
        joined = group["joined"]
        maxe = group["max"]
        pos = group["pos"]
        

        req = client.places.search(lat,lng)[0].to_dict()
        coords = req["geometry"]["coordinates"]
        lat, lng = coords[0] , coords[1]
        prop = req["properties"]
        new_name = prop["name"]
        addr, city, state = prop["address"], prop["city"], prop["province"]

        group_collection = db.Groups
        group_collection.update({"name":name},{"name":name,"joined":joined, "max":maxe, "pos":pos,"ll":{"lat":str(lat),"lng":str(lng),"name":new_name},"addr":addr, "city": city, "state":state, "finalized":1},upsert=True,safe=True)
        return {"ll":{"lat":lat,"lng":lng,"name":new_name},"addr":addr, "city": city, "state":state}


    def index(self):
        homepage_t = open('homepage.tmpl', 'r')
        self.homepage_template = homepage_t.read()
        return str(Template(self.homepage_template))
    index.exposed = True

    def add(self,name="",lat="",lng=""):
        group_collection = db.Groups
#        return str(self.group_exist(name))
        try:
            group_collection.update({"name":name},{"$push":{"pos":{"lat":str(lat),"lng":str(lng)}},"$inc":{"joined":1}},safe=True)
        except pymongo.errors.OperationFailure:
            return str(False)
        except:
            return str(False)
        
        group_t = open('group.tmpl', 'r')
        self.group_template = group_t.read()
        return str(Template(self.group_template, {"name":name}))        
    add.exposed = True

    def get_lat_lng(self,group = None):
        tups, num = group["pos"], int(group["max"])

        lngs, lats = [float(x["lng"]) for x in tups], [float(x["lat"]) for x in tups]
        avg_lng, avg_lat = reduce(lambda x,y:x+y,lngs)/num, reduce(lambda x,y:x+y,lats)/num
        return {"lat":avg_lat,"lng":avg_lng}

    def group_exist(self,name=""):
        if not (name==""):
            group_collection = db.Groups
            group = group_collection.find_one({"name":name})
            if group:
                if group["joined"] is not group["max"]:
                    #not full
                    return 1
                else:
                    #full
                    return 2
            else:
                return 0
        else:
            return -1

    def new(self,name="",number="",lat="",lng=""):
        g_exist = self.group_exist(name)
        if g_exist == 0:
            #group does not exist (good)
            group_collection = db.Groups
            try:
                group_collection.insert({"name":name,"joined":1,"max":int(number),"pos":[{"lat":lat,"lng":lng}],"finalized":0},safe=True)
            except pymongo.errors.OperationFailure:
                #error
                return "insert fucked up"
            except:
                #error
                return "something is really bad"
        
            group_t = open('group.tmpl', 'r')
            self.group_template = group_t.read()
            return str(Template(self.group_template, {"name":name}))
        elif g_exist > 0:
            #error page
            #group does exist (bad)
            #redirect to group page, tell error
            return "group already exists"
        elif g_exist == -1:
            #empty name
            return "Group is empty"
        else:
            #what the fuck
            return "Error!"
    new.exposed = True

cherrypy.quickstart(Index())
