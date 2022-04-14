import requests
import json



class API():

    def __init__(self,base_url,config):
        self.base_url = base_url
        with open(config,"r") as f:
            self.effects = json.loads(f.read())


    def post(self,data):
        try:
            resp = requests.post(self.base_url, json=data,timeout=5)
            return resp.status_code, resp.text
        except:
            print("Post exception")
            return 404,None


    def get_status(self):
        try:
            resp = requests.get(self.base_url,timeout=5)
            return resp.status_code, resp.json()
        except:
            print("Get exception")
            return 404,None

    def on_off(self,state):
        payload = {"on":state}
        status,resp = self.post(payload)
        if status == 200:
            return resp 
        else:
            return None

    def set_color(self,color,bri):
        b = 255 * (bri / 100)
        payload = {"on":True,"bri":int(b),"transition":7,"mainseg":0,
                   "seg":[{"id":0,"grp":1,"spc":0,"of":0,"on":True,"frz":False,"bri":255,"cct":127,
                   "col":[color,[0,0,0],[0,0,0]],"fx":0,"sx":128,"ix":128,"pal":0,"sel":True,"rev":False,"mi":False}]}
        status,resp = self.post(payload)
        if status == 200:
            return resp 
        else:
            return None

    def set_effect(self,effect):
        payload = self.effects[effect]
        status,resp = self.post(payload)
        if status == 200:
            return resp 
        else:
            return None




