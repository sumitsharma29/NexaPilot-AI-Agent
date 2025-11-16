
class TaskAgent:
    def __init__(self, memory, ask_llm_callable=None):
        self.memory = memory
        self.ask_llm = ask_llm_callable

    def add_task_raw(self, user_id, text):
        tasks = self.memory.get(user_id,"tasks") or []
        obj={"id":f"task_{len(tasks)+1}","title":text,"due":"","duration_min":60,"priority":"medium","completed":False}
        tasks.append(obj)
        self.memory.set(user_id,"tasks",tasks)
        return {"task":obj}

    def list_tasks(self,user_id):
        return self.memory.get(user_id,"tasks") or []
