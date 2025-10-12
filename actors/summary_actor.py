from thespian.actors import Actor
from crew_orchestrator import CrewOrchestrator
import traceback

class SummarizerActor(Actor):
    def receiveMessage(self, message, sender):
        if isinstance(message, dict) and message.get("cmd") == "summarize":
            try:
                topic = message.get("topic", "AI Trends")
                orchestrator = CrewOrchestrator()

                # Load and inject topic into prompt
                cfg = orchestrator.load_config("prompts/summarizer_agent.yaml")
                cfg["task"]["description"] = cfg["task"]["description"].replace("{{topic}}", topic)

                agent = orchestrator.create_agent(cfg)
                task = orchestrator.create_task(cfg, agent)
                result = task.execute_sync()

                summary = getattr(result, "raw", "") or getattr(result, "result", "")
                self.send(sender, {"status": "success", "stage": "summary", "topic": topic, "summary": summary})
            except Exception as e:
                self.send(sender, {"status": "error", "stage": "summary", "error": str(e), "trace": traceback.format_exc()})