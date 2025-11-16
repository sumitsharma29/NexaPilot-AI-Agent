
class RAGMemory:
    def __init__(self):
        self.store={}

    def set(self,uid,key,val):
        self.store.setdefault(uid,{})[key]=val

    def get(self,uid,key,default=None):
        return self.store.get(uid,{}).get(key,default)
