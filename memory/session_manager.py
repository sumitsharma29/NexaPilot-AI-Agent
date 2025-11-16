
class SessionManager:
    def __init__(self):
        self.sessions={}
    def start_session(self,uid):
        self.sessions[uid]={'turns':[]}
    def append_turn(self,uid,turn):
        self.sessions[uid]['turns'].append(turn)
