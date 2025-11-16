import os
import sys
import json

from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv

# Ensure root path is importable (for orchestrator, tools, memory, agents)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

# Load environment variables
load_dotenv()

# -------------------------------
# Gemini LLM Setup
# -------------------------------
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print("Gemini Model Load Error:", e)
    model = None

def ask(prompt: str):
    if not model:
        return "LLM Error: Model not initialized."

    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"LLM Error: {e}"


# -------------------------------
# Import Orchestrator + Tools
# -------------------------------
from orchestrator import Orchestrator
from tools.weather_tool import WeatherTool
from tools.search_tool import SearchTool

# Flask App
app = Flask(__name__, static_folder="static", template_folder="templates")

# Build Orchestrator with Tools
tools = {
    "weather": WeatherTool(),
    "search": SearchTool()
}

orch = Orchestrator(tools=tools, ask_llm_callable=ask)

# -------------------------------
# ROUTES
# -------------------------------

# Root → redirect to /chat
@app.route("/")
def home():
    return "<script>location.href='/chat'</script>"

# Chat UI page
@app.route("/chat")
def chat():
    return render_template("chat.html")


# Chat API (LLM + Agents)
@app.route("/api", methods=["POST"])
def api():
    data = request.get_json() or {}
    q = data.get("q", "")
    response = orch.handle("web", q)
    return jsonify({"response": response})


# -------------------------------
# TASKS ENDPOINTS (Right Panel)
# -------------------------------
@app.route("/tasks", methods=["GET"])
def tasks_list():
    uid = request.args.get("user", "web")
    try:
        tasks = orch.task_agent.list_tasks(uid)
    except Exception as e:
        return jsonify({"error": f"Task fetch error: {e}"}), 500

    return jsonify({"tasks": tasks})


@app.route("/tasks", methods=["POST"])
def tasks_add():
    uid = request.args.get("user", "web")
    payload = request.get_json() or {}
    text = payload.get("text") or payload.get("title") or ""

    if not text:
        return jsonify({"error": "Task text missing"}), 400

    try:
        out = orch.task_agent.add_task_raw(uid, text)
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": f"Task add error: {e}"}), 500


# -------------------------------
# WEATHER API (Used in Sidebar)
# -------------------------------
@app.route("/weather", methods=["GET"])
def weather():
    date = request.args.get("date") or ""
    try:
        advice = orch.info_agent.get_weather_advice("web", date)
        return jsonify({"advice": advice})
    except Exception as e:
        return jsonify({"advice": f"Weather error: {e}"})


# -------------------------------
# Static assets loader
# -------------------------------
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)


# -------------------------------
# Health Check
# -------------------------------
@app.route("/health")
def health():
    return "ok"


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(port=5000)
