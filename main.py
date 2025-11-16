
import os
from dotenv import load_dotenv
load_dotenv()

from tools.weather_tool import WeatherTool
from tools.search_tool import SearchTool
from orchestrator import Orchestrator

import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_llm(prompt: str) -> str:
    try:
        r = model.generate_content(prompt)
        return r.text
    except Exception as e:
        return f"LLM Error: {e}"

def main():
    weather = WeatherTool()
    search = SearchTool()
    tools = {"weather": weather, "search": search}
    orch = Orchestrator(tools=tools, ask_llm_callable=ask_llm)

    user_id = "user1"
    orch.start_user(user_id)

    print("Welcome to NexaPilot CLI. Type 'exit' to quit.")
    while True:
        user_input = input("\nYou> ").strip()
        if user_input.lower() in ("exit","quit"):
            print("Goodbye — NexaPilot signing off.")
            break
        resp = orch.handle(user_id, user_input)
        print("\nNexaPilot>", resp)

if __name__ == "__main__":
    main()
