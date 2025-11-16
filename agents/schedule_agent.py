
class ScheduleAgent:
    def __init__(self,memory,tools=None):
        self.memory=memory
        self.tools=tools or {}

    def suggest_day(self,user_id,date):
        tasks=self.memory.get(user_id,"tasks") or []
        out=[]
        base="2025-11-16T09:00:00"
        for t in tasks[:3]:
            out.append({"title":t["title"],"start":base,"end":"2025-11-16T10:00:00"})
        return out
