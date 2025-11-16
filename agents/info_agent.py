
class InfoAgent:
    def __init__(self,tools,memory):
        self.tools=tools
        self.memory=memory

    def get_weather_advice(self,user_id,date):
        return "Weather looks clear on "+date

    def quick_search(self,q):
        return {"top_result":{"title":"Demo","snippet":"Example search result"}}
