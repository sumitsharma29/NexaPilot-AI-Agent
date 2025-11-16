
from orchestrator import Orchestrator
from tools.weather_tool import WeatherTool
from tools.search_tool import SearchTool
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model=genai.GenerativeModel("gemini-2.5-flash")

def ask(p):
    try: return model.generate_content(p).text
    except: return "LLM error"

def run():
    t={"weather":WeatherTool(),"search":SearchTool()}
    orch=Orchestrator(t,ask)
    uid="eval"
    orch.start_user(uid)
    print(orch.handle(uid,"Add task: Finish project"))
    print(orch.handle(uid,"list tasks"))
    print(orch.handle(uid,"plan my day"))
    print(orch.handle(uid,"weather tomorrow"))

if __name__=="__main__":
    run()
