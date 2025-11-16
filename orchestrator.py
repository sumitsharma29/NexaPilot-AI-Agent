
import logging, time, json
from typing import Dict, Any

from agents.task_agent import TaskAgent
from agents.schedule_agent import ScheduleAgent
from agents.info_agent import InfoAgent
from memory.memory_bank_rag import RAGMemory
from memory.session_manager import SessionManager
from tools.observability import MetricsCollector

logger = logging.getLogger("nexapilot.orch")
logger.setLevel(logging.INFO)

class Orchestrator:
    def __init__(self, tools, ask_llm_callable, embeddings_callable=None):
        self.memory = RAGMemory()
        self.sessions = SessionManager()
        self.tools = tools
        self.ask_llm = ask_llm_callable
        self.get_embedding = embeddings_callable

        self.task_agent = TaskAgent(self.memory, ask_llm_callable=self.ask_llm)
        self.schedule_agent = ScheduleAgent(self.memory, tools=self.tools)
        self.info_agent = InfoAgent(self.tools, self.memory)

        self.metrics = MetricsCollector()

    def start_user(self, user_id: str):
        self.sessions.start_session(user_id)
        self.metrics.counter("sessions_started", 1)

    def append_turn(self, user_id: str, turn: Dict[str, Any]):
        self.sessions.append_turn(user_id, turn)

    def detect_intent(self, text):
        t = text.lower()
        if "add" in t and "task" in t: return {"intent":"add_task"}
        if "weather" in t: return {"intent":"get_weather"}
        if "plan" in t: return {"intent":"plan_day"}
        if "list" in t and "task" in t: return {"intent":"list_tasks"}
        return {"intent":"explain"}

    def handle(self, user_id: str, text: str):
        start = time.time()
        self.start_user(user_id)
        self.append_turn(user_id, {"role":"user","text":text,"ts":time.time()})

        intent = self.detect_intent(text)["intent"]

        if intent=="add_task":
            r=self.task_agent.add_task_raw(user_id,text)
            out=f"Added task: {r['task']['title']}"
        elif intent=="list_tasks":
            tasks=self.task_agent.list_tasks(user_id)
            out="\n".join([f"{t['id']} - {t['title']}" for t in tasks]) or "No tasks."
        elif intent=="get_weather":
            out=self.info_agent.get_weather_advice(user_id,"2025-11-16")
        elif intent=="plan_day":
            sched=self.schedule_agent.suggest_day(user_id,"2025-11-16")
            out="\n".join([f"- {s['title']} {s['start']} -> {s['end']}" for s in sched]) or "No schedule."
        else:
            out=self.ask_llm(f"You are NexaPilot. Answer: {text}")

        self.append_turn(user_id,{"role":"assistant","text":out,"ts":time.time()})
        self.metrics.timing("handle_latency_ms", (time.time()-start)*1000)
        return out
