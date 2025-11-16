
from prometheus_client import Counter, Summary

class MetricsCollector:
    def __init__(self):
        self.counters={"sessions_started":Counter("sessions_started","desc")}
        self.summaries={"handle_latency_ms":Summary("handle_latency_ms","desc")}
    def counter(self,n,i): self.counters[n].inc(i)
    def timing(self,n,v): self.summaries[n].observe(v)
